import json
import math
from datetime import date

# Django Core & Auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from django.db.models import F, Max, Q
from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView

# Local App Imports (Forms & Models)
from .forms import (
    SupplierForm, 
    RawMaterialInboundForm, 
    DailyProductionItemForm
)
from .models import (
    Supplier,
    Purchase, 
    PurchaseItem, 
    RawMaterial, 
    ProductVariant, 
    DailyProduction, 
    DailyProductionItem,
    DailyProductionRawItem, 
    ProductType,
)

class InboundsListView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'inventory.view_purchase'
    raise_exception     = True

    def get(self, request):
        qs = (
            PurchaseItem.objects
            .select_related('purchase__supplier', 'raw_material')
            .order_by('-purchase__receive_date', '-purchase__pk')
        )

        # --- Filters ---
        q_supplier = request.GET.get('supplier', '').strip()
        q_date     = request.GET.get('date', '').strip()
        q_search   = request.GET.get('search', '').strip()

        if q_supplier:
            qs = qs.filter(purchase__supplier__name__icontains=q_supplier)
        if q_date:
            qs = qs.filter(purchase__receive_date=q_date)
        if q_search:
            qs = qs.filter(raw_material__name__icontains=q_search)

        # --- Pagination ---
        paginator = Paginator(qs, 6)
        page_num  = request.GET.get('page', 1)
        page_obj  = paginator.get_page(page_num)

        # Supplier list for filter dropdown
        all_suppliers = Supplier.objects.order_by('name')

        # Raw material stock list
        raw_materials = RawMaterial.objects.all().order_by('name')

        return render(request, 'inbounds.html', {
            'page_obj':      page_obj,
            'all_suppliers': all_suppliers,
            'q_supplier':    q_supplier,
            'q_date':        q_date,
            'q_search':      q_search,
            'raw_materials': raw_materials,
            'is_warehouse':  request.user.groups.filter(name='Warehouse').exists(),
        })


class InboundAddView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'inventory.add_purchase'
    raise_exception     = True

    def _build_context(self, formset, raw_materials, units_map, raw_materials_json, suppliers_json):
        return {
            'formset':            formset,
            'units_map_json':     json.dumps(units_map),
            'raw_materials_json': json.dumps(raw_materials_json),
            'suppliers_json':     json.dumps(suppliers_json),
        }

    def _load_form_data(self):
        raw_materials      = RawMaterial.objects.all()
        suppliers          = Supplier.objects.all()
        units_map          = {rm.pk: rm.unit for rm in raw_materials}
        raw_materials_json = [{'id': rm.pk, 'name': rm.name, 'unit': rm.unit} for rm in raw_materials]
        suppliers_json     = [{'id': s.pk, 'name': s.name} for s in suppliers]
        return raw_materials, suppliers, units_map, raw_materials_json, suppliers_json

    def get(self, request):
        raw_materials, suppliers, units_map, raw_materials_json, suppliers_json = self._load_form_data()
        InboundFormSet = formset_factory(RawMaterialInboundForm, extra=1, can_delete=False)
        formset = InboundFormSet(prefix='inbound')
        return render(request, 'inbound_add.html',
                      self._build_context(formset, raw_materials, units_map, raw_materials_json, suppliers_json))

    def post(self, request):
        raw_materials, suppliers, units_map, raw_materials_json, suppliers_json = self._load_form_data()
        InboundFormSet = formset_factory(RawMaterialInboundForm, extra=1, can_delete=False)
        formset = InboundFormSet(request.POST, prefix='inbound')

        if not formset.is_valid():
            return render(request, 'inbound_add.html',
                          self._build_context(formset, raw_materials, units_map, raw_materials_json, suppliers_json))

        # Process only non-empty forms
        valid_forms = [f for f in formset.forms if f.cleaned_data and any(f.cleaned_data.values())]

        if not valid_forms:
            messages.error(request, 'Silakan isi minimal satu transaksi barang masuk.')
            return render(request, 'inbound_add.html',
                          self._build_context(formset, raw_materials, units_map, raw_materials_json, suppliers_json))

        # Save all valid transactions
        for form in valid_forms:
            data         = form.cleaned_data
            raw_material = data['raw_material']
            supplier     = data['supplier']
            quantity     = data['quantity']
            receive_date = data['receive_date']

            _temp_user = request.user if request.user.is_authenticated \
                         else get_user_model().objects.first()

            purchase = Purchase.objects.create(
                supplier=supplier,
                total_price=0,
                purchase_date=receive_date,
                receive_date=receive_date,
                who_inputs=_temp_user,
            )
            PurchaseItem.objects.create(
                purchase=purchase,
                raw_material=raw_material,
                quantity=quantity,
                subtotal_price=0,
            )

            # Update stock & last restocked date
            # Use F() to avoid overwriting stale values when the same raw
            # material appears in multiple cards of the same formset.
            raw_material.qty_in_stock = F('qty_in_stock') + quantity
            raw_material.last_restocked = receive_date
            raw_material.save(update_fields=['qty_in_stock', 'last_restocked'])

            # Update supplier last transaction date
            supplier.last_transaction = receive_date
            supplier.save(update_fields=['last_transaction'])

        count = len(valid_forms)
        messages.success(request, f'Berhasil menambahkan {count} transaksi barang masuk.')
        return redirect('inventory:inbounds')


class InboundDetailView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'inventory.view_purchase'
    raise_exception     = True

    def get(self, request, pk):
        item = get_object_or_404(
            PurchaseItem.objects.select_related(
                'purchase__supplier',
                'purchase__who_inputs',
                'raw_material',
            ),
            pk=pk,
        )
        return render(request, 'inbound_detail.html', {'item': item})


class InboundDeleteView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Soft-delete: mark Purchase as inactive and roll back raw material stock."""
    permission_required = 'inventory.delete_purchase'
    raise_exception     = True

    def post(self, request, pk):
        item = get_object_or_404(
            PurchaseItem.objects.select_related('purchase', 'raw_material'),
            pk=pk,
        )

        if not item.purchase.is_active:
            messages.error(request, 'Transaksi ini sudah tidak aktif.')
            return redirect('inventory:inbound-detail', pk=pk)

        with db_transaction.atomic():
            # Roll back raw material stock
            item.raw_material.qty_in_stock = F('qty_in_stock') - item.quantity
            item.raw_material.save(update_fields=['qty_in_stock'])

            # Soft-delete the purchase
            item.purchase.is_active = False
            item.purchase.save(update_fields=['is_active'])

        messages.success(request, 'Transaksi berhasil dihapus dan stok bahan baku telah dikembalikan.')
        return redirect('inventory:inbounds')


# ─────────────────────────────────────────────────────────────────────────────
# Daily Production
# ─────────────────────────────────────────────────────────────────────────────

# Raw material name constants (must match fixture data)
_RM_GARAM   = 'Garam Krosok'
_RM_IODIUM  = 'Iodium'
_RM_PLASTIK = 'Plastik'
_RM_KARUNG  = 'Karung'

# Variants with size_grams equal to this value use karung packaging;
# all other variants (gram-sized) use plastik.
_KARUNG_SIZE_GRAMS = 50_000  # 50 kg


class ProductionAddView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'inventory.add_dailyproduction'
    raise_exception     = True
    TEMPLATE            = 'production_add.html'
    FORMSET_PREFIX = 'prod'

    # ── helpers ──────────────────────────────────────────────────────────────
    def _variants_json(self):
        return [
            {'id': v.pk, 'product_type': v.product_type, 'size_grams': v.size_grams}
            for v in ProductVariant.objects.all().order_by('product_type', 'size_grams')
        ]

    def _render(self, request, formset, variants_json):
        return render(request, self.TEMPLATE, {
            'formset':       formset,
            'variants_json': json.dumps(variants_json),
        })

    # ── GET ───────────────────────────────────────────────────────────────────
    def get(self, request):
        FormSet = formset_factory(DailyProductionItemForm, extra=1, can_delete=False)
        formset = FormSet(prefix=self.FORMSET_PREFIX)
        return self._render(request, formset, self._variants_json())

    # ── POST ──────────────────────────────────────────────────────────────────
    def post(self, request):
        vj     = self._variants_json()
        FormSet = formset_factory(DailyProductionItemForm, extra=1, can_delete=False)
        formset = FormSet(request.POST, prefix=self.FORMSET_PREFIX)

        if not formset.is_valid():
            return self._render(request, formset, vj)

        valid_forms = [
            f for f in formset.forms
            if f.cleaned_data and any(f.cleaned_data.values())
        ]
        if not valid_forms:
            messages.error(request, 'Silakan isi minimal satu item produksi.')
            return self._render(request, formset, vj)

        # Check for duplicate variants in submission
        submitted_variants = [f.cleaned_data['product_variant'] for f in valid_forms
                              if f.cleaned_data.get('product_variant')]
        if len(submitted_variants) != len(set(v.pk for v in submitted_variants)):
            messages.error(request, 'Varian produk tidak boleh duplikat dalam satu sesi produksi.')
            return self._render(request, formset, vj)

        # TODO: hapus fallback _temp_user setelah fitur autentikasi selesai
        _temp_user = request.user if request.user.is_authenticated \
                     else get_user_model().objects.first()

        try:
            with db_transaction.atomic():
                # Fetch raw materials (fail early if data missing)
                try:
                    rm_garam   = RawMaterial.objects.select_for_update().get(name=_RM_GARAM)
                    rm_iodium  = RawMaterial.objects.select_for_update().get(name=_RM_IODIUM)
                    rm_plastik = RawMaterial.objects.select_for_update().get(name=_RM_PLASTIK)
                    rm_karung  = RawMaterial.objects.select_for_update().get(name=_RM_KARUNG)
                except RawMaterial.DoesNotExist as exc:
                    raise ValueError(f'Data bahan baku tidak ditemukan: {exc}') from exc

                # Calculate total deductions
                total_garam       = 0
                total_garam_kasar = 0   # subset used for Iodium calculation
                total_plastik     = 0
                total_karung      = 0
                items_data        = []

                for form in valid_forms:
                    d       = form.cleaned_data
                    variant = d['product_variant']
                    qty     = d['quantity']
                    prod_dt = d.get('production_date') or date.today()

                    # Garam Krosok: ceil(qty × size_grams / 1000) kg
                    garam_kg = math.ceil(qty * variant.size_grams / 1000)
                    total_garam += garam_kg

                    # Packaging: karung for 50 kg variants, plastik for all gram-sized variants
                    if variant.size_grams == _KARUNG_SIZE_GRAMS:
                        total_karung  += qty
                    else:
                        total_plastik += qty

                    # Iodium is used only for Kasar (Hard) products
                    if variant.product_type == ProductType.HARD:
                        total_garam_kasar += garam_kg

                    items_data.append((variant, qty, prod_dt, garam_kg))

                # Iodium: 1 kg per 20 ton (20 000 kg) of Garam Krosok used for Kasar
                total_iodium = math.ceil(total_garam_kasar / 20_000) if total_garam_kasar else 0

                # Stock sufficiency checks
                if rm_garam.qty_in_stock < total_garam:
                    raise ValueError(
                        f'Stok {_RM_GARAM} tidak cukup. '
                        f'Dibutuhkan: {total_garam} kg, tersedia: {rm_garam.qty_in_stock} kg.')
                if total_iodium and rm_iodium.qty_in_stock < total_iodium:
                    raise ValueError(
                        f'Stok {_RM_IODIUM} tidak cukup. '
                        f'Dibutuhkan: {total_iodium} kg, tersedia: {rm_iodium.qty_in_stock} kg.')
                if total_plastik and rm_plastik.qty_in_stock < total_plastik:
                    raise ValueError(
                        f'Stok {_RM_PLASTIK} tidak cukup. '
                        f'Dibutuhkan: {total_plastik} pcs, tersedia: {rm_plastik.qty_in_stock} pcs.')
                if total_karung and rm_karung.qty_in_stock < total_karung:
                    raise ValueError(
                        f'Stok {_RM_KARUNG} tidak cukup. '
                        f'Dibutuhkan: {total_karung} pcs, tersedia: {rm_karung.qty_in_stock} pcs.')

                # Create DailyProduction header (use date of first item)
                production_date = items_data[0][2]
                daily_prod = DailyProduction.objects.create(
                    production_date=production_date,
                    who_inputs=_temp_user,
                )

                # Create items & update ProductVariant stock
                for variant, qty, prod_dt, garam_kg in items_data:
                    DailyProductionItem.objects.create(
                        daily_production=daily_prod,
                        product_variant=variant,
                        quantity=qty,
                    )
                    variant.qty_in_stock += qty
                    variant.save(update_fields=['qty_in_stock'])

                # Deduct raw materials & record usage
                rm_garam.qty_in_stock -= total_garam
                rm_garam.save(update_fields=['qty_in_stock'])
                DailyProductionRawItem.objects.create(
                    daily_production=daily_prod, raw_material=rm_garam, quantity=total_garam)

                if total_iodium:
                    rm_iodium.qty_in_stock -= total_iodium
                    rm_iodium.save(update_fields=['qty_in_stock'])
                    DailyProductionRawItem.objects.create(
                        daily_production=daily_prod, raw_material=rm_iodium, quantity=total_iodium)

                if total_plastik:
                    rm_plastik.qty_in_stock -= total_plastik
                    rm_plastik.save(update_fields=['qty_in_stock'])
                    DailyProductionRawItem.objects.create(
                        daily_production=daily_prod, raw_material=rm_plastik, quantity=total_plastik)

                if total_karung:
                    rm_karung.qty_in_stock -= total_karung
                    rm_karung.save(update_fields=['qty_in_stock'])
                    DailyProductionRawItem.objects.create(
                        daily_production=daily_prod, raw_material=rm_karung, quantity=total_karung)

        except ValueError as exc:
            messages.error(request, str(exc))
            return self._render(request, formset, vj)

        messages.success(
            request,
            f'Berhasil mencatat {len(valid_forms)} item produksi harian.'
        )
        return redirect('inventory:production')


# ─────────────────────────────────────────────────────────────────────────────
# Barang Jadi (Production List)
# ─────────────────────────────────────────────────────────────────────────────

class ProductionListView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'inventory.view_dailyproduction'
    raise_exception     = True

    def get(self, request):
        # ── Section 1: ProductVariant stock ──────────────────────────────────
        variants = (
            ProductVariant.objects
            .annotate(last_produced=Max('daily_production_items__daily_production__production_date'))
            .order_by('product_type', 'size_grams')
        )

        # ── Section 2: DailyProductionItem records ────────────────────────────
        items_qs = (
            DailyProductionItem.objects
            .select_related('daily_production', 'product_variant')
            .order_by('-daily_production__production_date', '-daily_production__pk')
        )

        # --- Filters ---
        q_search = request.GET.get('search', '').strip()
        q_date   = request.GET.get('date', '').strip()
        q_type   = request.GET.get('product_type', '').strip()

        if q_search:
            # Map Indonesian display labels to stored type codes so that
            # searching "halus" or "garam halus" correctly hits SOFT records,
            # and "kasar" / "garam kasar" correctly hits HARD records.
            _TYPE_MAP = {
                'halus': 'SOFT', 'soft': 'SOFT',
                'kasar': 'HARD', 'hard': 'HARD',
            }
            s = q_search.lower()
            matched_type = next((code for key, code in _TYPE_MAP.items() if key in s), None)

            size_q = Q()
            try:
                size_q = Q(product_variant__size_grams=int(q_search))
            except ValueError:
                pass

            type_q = Q(product_variant__product_type=matched_type) if matched_type \
                     else Q(product_variant__product_type__icontains=q_search)

            items_qs = items_qs.filter(size_q | type_q)
        if q_date:
            items_qs = items_qs.filter(daily_production__production_date=q_date)
        if q_type:
            items_qs = items_qs.filter(product_variant__product_type=q_type)

        # --- Pagination ---
        var_paginator = Paginator(variants, 5)
        var_page_obj  = var_paginator.get_page(request.GET.get('var_page', 1))

        paginator = Paginator(items_qs, 6)
        page_num  = request.GET.get('page', 1)
        page_obj  = paginator.get_page(page_num)

        return render(request, 'production.html', {
            'var_page_obj': var_page_obj,
            'page_obj':     page_obj,
            'q_search':     q_search,
            'q_date':       q_date,
            'q_type':       q_type,
            'is_warehouse': request.user.groups.filter(name='Warehouse').exists(),
        })
    
class SupplierListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Menampilkan daftar supplier dengan fitur filter, sorting, dan pagination."""

    template_name = 'supplier/supplier_list.html'
    permission_required = 'inventory.view_supplier'

    def get_context_data(self, **kwargs):
        """Menyusun context halaman list berdasarkan query parameter dari URL.

        Query parameter yang didukung:
        - q: pencarian nama supplier (contains, case-insensitive)
        - status: aktif | nonaktif
        - sort: name | created_at | status
        - order: asc | desc
        """
        context = super().get_context_data(**kwargs)
        request = self.request
        suppliers = Supplier.objects.all()
        q = request.GET.get('q', '').strip()
        status = request.GET.get('status', '')
        sort = request.GET.get('sort', 'created_at')
        order = request.GET.get('order', 'desc')
        if q:
            suppliers = suppliers.filter(name__icontains=q)
        if status == 'aktif':
            suppliers = suppliers.filter(is_active=True)
        elif status == 'nonaktif':
            suppliers = suppliers.filter(is_active=False)
        sort_fields = {
            'name': 'name',
            'created_at': 'created_at',
            'status': 'is_active',
        }
        sort_field = sort_fields.get(sort, 'created_at')
        if order == 'asc':
            suppliers = suppliers.order_by(sort_field)
        else:
            suppliers = suppliers.order_by('-' + sort_field)
        paginator = Paginator(suppliers, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['suppliers'] = page_obj
        context['page_obj'] = page_obj
        context['sort'] = sort
        context['order'] = order
        return context

class SupplierCreateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Menangani pembuatan supplier baru."""

    template_name = 'supplier/supplier_create.html'
    permission_required = 'inventory.add_supplier'

    def get_context_data(self, **kwargs):
        """Menyediakan form kosong (atau form invalid yang dikirim ulang)."""
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs.get('form') or SupplierForm()
        return context

    def post(self, request, *args, **kwargs):
        """Validasi dan simpan supplier dengan pengecekan duplikasi nama."""
        form = SupplierForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Supplier.objects.filter(name__iexact=name).exists():
                form.add_error('name', 'Nama supplier sudah terdaftar di sistem.')
                return self.render_to_response(self.get_context_data(form=form))
            supplier = form.save(commit=False)
            supplier.is_active = True
            supplier.save()
            messages.success(request, 'Supplier berhasil ditambahkan!')
            return redirect('inventory:supplier')
        return self.render_to_response(self.get_context_data(form=form))

class SupplierUpdateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Menangani pembaruan data supplier existing."""

    template_name = 'supplier/supplier_update.html'
    permission_required = 'inventory.change_supplier'

    def get_context_data(self, **kwargs):
        """Mengambil supplier berdasarkan pk dan menyiapkan form edit."""
        context = super().get_context_data(**kwargs)
        pk = kwargs.get('pk')
        supplier = get_object_or_404(Supplier, pk=pk)
        context['supplier'] = supplier
        context['form'] = kwargs.get('form') or SupplierForm(instance=supplier)
        return context

    def post(self, request, *args, **kwargs):
        """Memproses update supplier dengan validasi nama unik dan status aktif."""
        pk = kwargs.get('pk')
        supplier = get_object_or_404(Supplier, pk=pk)
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Supplier.objects.filter(name__iexact=name).exclude(pk=pk).exists():
                form.add_error('name', 'Nama supplier sudah terdaftar di sistem.')
                return self.render_to_response(self.get_context_data(form=form, pk=pk))
            supplier = form.save(commit=False)
            supplier.is_active = request.POST.get('is_active') == '1'
            supplier.save()
            messages.success(request, 'Supplier berhasil diperbarui!')
            return redirect('inventory:supplier')
        return self.render_to_response(self.get_context_data(form=form, pk=pk))