from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Supplier
from .forms import SupplierForm

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