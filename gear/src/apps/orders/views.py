from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, F
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    Customer, CustomerStatus, Order, OrderItem, OrderStatus,
    PaymentStatus, PaymentMethod, OrderHistory, OrderChangeType
)
from .forms import CustomerForm, OrderForm, OrderItemFormSet

import json


# ──────────────────────────────────────
# RBAC HELPER FUNCTIONS
# ──────────────────────────────────────

def can_view_orders(user):
    """Check if user has permission to view orders"""
    if user.is_superuser:
        return True
    allowed_groups = {'Sales', 'Warehouse', 'Finance'}
    return user.groups.filter(name__in=allowed_groups).exists()


def can_create_or_edit_orders(user):
    """Check if user has permission to create/edit orders"""
    if user.is_superuser:
        return True
    return user.groups.filter(name='Sales').exists()


def check_view_permission(view_func):
    """Decorator to check view permission for orders"""
    def wrapper(request, *args, **kwargs):
        if not can_view_orders(request.user):
            messages.error(request, 'Anda tidak memiliki akses untuk melihat pesanan.')
            return redirect('orders:pemesanan-operasional')
        return view_func(request, *args, **kwargs)
    return wrapper


def check_create_or_edit_permission(view_func):
    """Decorator to check create/edit permission for orders"""
    def wrapper(request, *args, **kwargs):
        if not can_create_or_edit_orders(request.user):
            messages.error(request, 'Anda tidak memiliki izin untuk membuat atau mengedit pesanan.')
            return redirect('orders:pemesanan-operasional')
        return view_func(request, *args, **kwargs)
    return wrapper


# ──────────────────────────────────────
# ORDER VIEWS (PBI 15-20)
# ──────────────────────────────────────

@login_required
@check_view_permission
def order_list(request):
    """PBI-16: Daftar Pesanan dengan filter, search, pagination"""
    orders = Order.objects.select_related('customer', 'who_inputs').prefetch_related('items')

    # RBAC: Sales hanya lihat order sendiri, Others lihat semua
    if not request.user.is_superuser and request.user.groups.filter(name='Sales').exists():
        orders = orders.filter(who_inputs=request.user)

    # Filter: status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    # Filter: date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        orders = orders.filter(order_date__gte=date_from)
    if date_to:
        orders = orders.filter(order_date__lte=date_to)

    # Filter: sales (admin only)
    sales_filter = request.GET.get('sales', '')
    if sales_filter and (request.user.is_superuser or not request.user.groups.filter(name='Sales').exists()):
        orders = orders.filter(who_inputs_id=sales_filter)

    # Search: order_number or customer name
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    # Annotate item count
    orders = orders.annotate(item_count=Count('items'))

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)
    try:
        orders_page = paginator.page(page)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)

    # Get sales users for filter dropdown (admin only)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    sales_users = User.objects.filter(groups__name='Sales', is_active=True).order_by('first_name')

    context = {
        'orders': orders_page,
        'paginator': paginator,
        'status_choices': OrderStatus.choices,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sales_filter': sales_filter,
        'search_query': search_query,
        'sales_users': sales_users,
        'is_admin': request.user.is_superuser or not request.user.groups.filter(name='Sales').exists(),
        'can_create': can_create_or_edit_orders(request.user),
    }
    return render(request, 'orders/order_list.html', context)


@login_required
@check_view_permission
def order_detail(request, pk):
    """PBI-17: Detail Pesanan"""
    order = get_object_or_404(
        Order.objects.select_related('customer', 'who_inputs').prefetch_related('items__product_variant'),
        pk=pk
    )

    # RBAC: Sales hanya bisa lihat order sendiri
    if not request.user.is_superuser and request.user.groups.filter(name='Sales').exists():
        if order.who_inputs != request.user:
            messages.error(request, 'Anda tidak memiliki akses ke pesanan ini.')
            return redirect('orders:pemesanan-operasional')

    items = order.items.select_related('product_variant').all()
    history = order.history.select_related('changed_by').all()

    # Determine which status transitions are allowed
    # can_edit: only if status is REQUESTED AND user has edit permission (owner/Sales who owns the order)
    can_edit_permission = can_create_or_edit_orders(request.user) and (request.user.is_superuser or order.who_inputs == request.user)
    can_edit = can_edit_permission and order.order_status == OrderStatus.REQUESTED
    
    # can_cancel: only if status is REQUESTED AND user is the owner or admin
    can_cancel_permission = request.user.is_superuser or order.who_inputs == request.user
    can_cancel = can_cancel_permission and order.order_status == OrderStatus.REQUESTED
    
    is_warehouse_or_admin = request.user.is_superuser or request.user.groups.filter(name='Warehouse').exists()

    # Next possible statuses for warehouse/admin
    status_transitions = []
    if is_warehouse_or_admin:
        if order.order_status == OrderStatus.REQUESTED:
            status_transitions.append(('IN_PROGRESS', 'Proses Pesanan'))
        elif order.order_status == OrderStatus.CONFIRMED:
            status_transitions.append(('IN_SHIPPING', 'Kirim Pesanan'))
        elif order.order_status == OrderStatus.IN_SHIPPING:
            status_transitions.append(('DELIVERED', 'Tandai Diterima'))
        elif order.order_status == OrderStatus.DELIVERED:
            status_transitions.append(('COMPLETED', 'Selesaikan'))

    context = {
        'order': order,
        'items': items,
        'history': history,
        'can_edit': can_edit,
        'can_cancel': can_cancel,
        'is_warehouse_or_admin': is_warehouse_or_admin,
        'status_transitions': status_transitions,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@check_create_or_edit_permission
def order_create(request):
    """PBI-15: Membuat Pesanan Baru"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Create order
                order = form.save(commit=False)
                order.who_inputs = request.user
                order.order_status = OrderStatus.REQUESTED
                order.save()  # This auto-generates order_number

                # Save items
                formset.instance = order
                items = formset.save(commit=False)

                total_price = 0
                for item in items:
                    # Auto-fill price from variant if not specified
                    if not item.unit_price:
                        item.unit_price = item.product_variant.default_price
                    item.subtotal = item.quantity * item.unit_price
                    item.save()
                    total_price += item.subtotal

                    # Reserve stock
                    variant = item.product_variant
                    variant.reserved_stock = F('reserved_stock') + item.quantity
                    variant.save(update_fields=['reserved_stock'])

                # Update order total
                order.total_price = total_price
                Order.objects.filter(pk=order.pk).update(total_price=total_price)

                # Audit log
                OrderHistory.objects.create(
                    order=order,
                    changed_by=request.user,
                    change_type=OrderChangeType.CREATED,
                    new_values={
                        'order_number': order.order_number,
                        'customer': str(order.customer),
                        'total_price': total_price,
                        'items_count': len(items),
                    },
                )

            messages.success(request, f'Pesanan {order.order_number} berhasil dibuat!')
            return redirect('orders:order-detail', pk=order.pk)
        else:
            messages.error(request, 'Gagal membuat pesanan. Periksa form kembali.')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    # Build variant data for JS auto-fill
    from apps.inventory.models import ProductVariant
    variants = ProductVariant.objects.all()
    variant_prices = {v.pk: v.default_price for v in variants}

    context = {
        'form': form,
        'formset': formset,
        'variant_prices': json.dumps(variant_prices),
        'title': 'Buat Pesanan Baru',
        'submit_label': 'Simpan Pesanan',
    }
    return render(request, 'orders/order_form.html', context)


@login_required
@check_create_or_edit_permission
def order_edit(request, pk):
    """PBI-18: Memperbarui Pesanan (hanya status MENGAJUKAN)"""
    order = get_object_or_404(Order.objects.select_related('customer', 'who_inputs'), pk=pk)

    # Validate status
    if order.order_status != OrderStatus.REQUESTED:
        messages.error(request, 'Pesanan sudah diproses dan tidak dapat diedit.')
        return redirect('orders:order-detail', pk=order.pk)

    # RBAC: Only order creator or admin
    if not request.user.is_superuser and order.who_inputs != request.user:
        messages.error(request, 'Anda tidak memiliki akses untuk mengedit pesanan ini.')
        return redirect('orders:pemesanan-operasional')

    # Capture old values for audit
    old_items = list(order.items.values('product_variant_id', 'quantity', 'unit_price', 'subtotal'))
    old_total = order.total_price

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Release old reserved stock
                for item in order.items.select_related('product_variant').all():
                    variant = item.product_variant
                    variant.reserved_stock = F('reserved_stock') - item.quantity
                    variant.save(update_fields=['reserved_stock'])

                # Save order
                order = form.save()

                # Save items (handles add/update/delete)
                items = formset.save(commit=False)

                # Delete removed items
                for deleted_item in formset.deleted_objects:
                    deleted_item.delete()

                total_price = 0
                for item in items:
                    if not item.unit_price:
                        item.unit_price = item.product_variant.default_price
                    item.subtotal = item.quantity * item.unit_price
                    item.save()
                    total_price += item.subtotal

                    # Reserve new stock
                    variant = item.product_variant
                    variant.reserved_stock = F('reserved_stock') + item.quantity
                    variant.save(update_fields=['reserved_stock'])

                # Also account for existing items that weren't changed
                for existing_item in order.items.exclude(pk__in=[i.pk for i in items] + [d.pk for d in formset.deleted_objects]):
                    total_price += existing_item.subtotal
                    # Re-reserve stock for untouched items
                    variant = existing_item.product_variant
                    variant.reserved_stock = F('reserved_stock') + existing_item.quantity
                    variant.save(update_fields=['reserved_stock'])

                # Update total
                order.total_price = total_price
                Order.objects.filter(pk=order.pk).update(total_price=total_price)

                # Audit
                new_items = list(order.items.values('product_variant_id', 'quantity', 'unit_price', 'subtotal'))
                OrderHistory.objects.create(
                    order=order,
                    changed_by=request.user,
                    change_type=OrderChangeType.UPDATED,
                    old_values={'items': old_items, 'total_price': old_total},
                    new_values={'items': new_items, 'total_price': total_price},
                )

            messages.success(request, f'Pesanan {order.order_number} berhasil diperbarui!')
            return redirect('orders:order-detail', pk=order.pk)
        else:
            messages.error(request, 'Gagal memperbarui pesanan. Periksa form kembali.')
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    from apps.inventory.models import ProductVariant
    variants = ProductVariant.objects.all()
    variant_prices = {v.pk: v.default_price for v in variants}

    context = {
        'form': form,
        'formset': formset,
        'variant_prices': json.dumps(variant_prices),
        'order': order,
        'title': f'Edit Pesanan {order.order_number}',
        'submit_label': 'Simpan Perubahan',
        'is_edit': True,
    }
    return render(request, 'orders/order_form.html', context)


@login_required
@check_view_permission
def order_update_status(request, pk):
    """PBI-19: Memperbarui Status Pesanan (Warehouse/Admin only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    order = get_object_or_404(Order.objects.prefetch_related('items__product_variant'), pk=pk)

    # RBAC: Only Warehouse or Admin
    if not request.user.is_superuser and not request.user.groups.filter(name='Warehouse').exists():
        messages.error(request, 'Anda tidak memiliki izin untuk mengubah status pesanan.')
        return redirect('orders:pemesanan-operasional')

    new_status = request.POST.get('new_status')
    valid_statuses = [s[0] for s in OrderStatus.choices]
    if new_status not in valid_statuses:
        messages.error(request, 'Status tidak valid.')
        return redirect('orders:order-detail', pk=order.pk)

    old_status = order.order_status

    # Validate transition
    valid_transitions = {
        'REQUESTED': ['IN_PROGRESS', 'CANCELLED'],
        'IN_PROGRESS': ['IN_SHIPPING'],
        'IN_SHIPPING': ['DELIVERED'],
        'DELIVERED': ['COMPLETED'],
    }

    if new_status not in valid_transitions.get(old_status, []):
        messages.error(request, f'Transisi status dari {order.get_order_status_display()} ke status tersebut tidak diizinkan.')
        return redirect('orders:order-detail', pk=order.pk)

    with transaction.atomic():
        # If moving to IN_PROGRESS: deduct from actual stock, release reserved
        if new_status == 'IN_PROGRESS':
            for item in order.items.select_related('product_variant').all():
                variant = item.product_variant
                if variant.qty_in_stock < item.quantity:
                    messages.error(
                        request,
                        f'Stok tidak mencukupi untuk {variant}. '
                        f'Tersedia: {variant.qty_in_stock}, Dibutuhkan: {item.quantity}'
                    )
                    return redirect('orders:order-detail', pk=order.pk)

                variant.qty_in_stock = F('qty_in_stock') - item.quantity
                variant.reserved_stock = F('reserved_stock') - item.quantity
                variant.save(update_fields=['qty_in_stock', 'reserved_stock'])

        # If delivered, record delivery date
        if new_status == 'DELIVERED':
            from datetime import date
            order.date_delivered = date.today()

        order.order_status = new_status
        order.save(update_fields=['order_status', 'date_delivered'] if new_status == 'DELIVERED' else ['order_status'])

        # Audit
        OrderHistory.objects.create(
            order=order,
            changed_by=request.user,
            change_type=OrderChangeType.STATUS_CHANGED,
            old_values={'status': old_status},
            new_values={'status': new_status},
        )

    status_display = dict(OrderStatus.choices).get(new_status, new_status)
    messages.success(request, f'Status pesanan {order.order_number} berhasil diubah menjadi {status_display}.')
    return redirect('orders:order-detail', pk=order.pk)


@login_required
@check_view_permission
def order_cancel(request, pk):
    """PBI-20: Membatalkan Pesanan (Soft Delete)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    order = get_object_or_404(Order.objects.prefetch_related('items__product_variant'), pk=pk)

    # RBAC: Only order creator or admin
    if not request.user.is_superuser and order.who_inputs != request.user:
        messages.error(request, 'Anda tidak memiliki akses untuk membatalkan pesanan ini.')
        return redirect('orders:pemesanan-operasional')

    # Validate status
    if order.order_status != OrderStatus.REQUESTED:
        messages.error(request, 'Pesanan sudah diproses, tidak dapat dibatalkan.')
        return redirect('orders:order-detail', pk=order.pk)

    with transaction.atomic():
        # Release reserved stock
        for item in order.items.select_related('product_variant').all():
            variant = item.product_variant
            variant.reserved_stock = F('reserved_stock') - item.quantity
            variant.save(update_fields=['reserved_stock'])

        # Soft delete: change status to CANCELLED
        old_status = order.order_status
        order.order_status = OrderStatus.CANCELLED
        order.save(update_fields=['order_status'])

        # Audit
        OrderHistory.objects.create(
            order=order,
            changed_by=request.user,
            change_type=OrderChangeType.CANCELLED,
            old_values={'status': old_status},
            new_values={'status': OrderStatus.CANCELLED},
            notes=f'Pesanan dibatalkan oleh {request.user.get_full_name()}'
        )

    messages.success(request, f'Pesanan {order.order_number} berhasil dibatalkan.')
    return redirect('orders:order-list')


# ──────────────────────────────────────
# PRODUCT VARIANT API (for dynamic form)
# ──────────────────────────────────────

@login_required
def variant_price_api(request):
    """API endpoint to get variant prices for the order form JS"""
    from apps.inventory.models import ProductVariant
    variants = ProductVariant.objects.all()
    data = {
        v.pk: {
            'price': v.default_price,
            'label': str(v),
            'stock': v.available_stock,
        }
        for v in variants
    }
    return JsonResponse(data)


@login_required
@check_view_permission
def customer_list(request):
    """List all customers with filtering and search"""
    # Get filter parameters
    show_inactive = request.GET.get('show_inactive', 'false') == 'true'
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Base queryset
    customers = Customer.objects.select_related('sales_pic').all()
    
    # Apply status filter
    if not show_inactive:
        customers = customers.filter(status=CustomerStatus.ACTIVE)
    
    # Apply search filter
    if search_query:
        customers = customers.filter(
            Q(customer_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Pagination - 10 items per page
    paginator = Paginator(customers, 10)
    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        customers_page = paginator.page(1)
    except EmptyPage:
        customers_page = paginator.page(paginator.num_pages)
    
    context = {
        'customers': customers_page,
        'show_inactive': show_inactive,
        'search_query': search_query,
        'paginator': paginator,
    }
    
    return render(request, 'orders/customer_list.html', context)


@login_required
@check_create_or_edit_permission
def customer_add(request):
    """Add new customer - GET to show form, POST to save"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer {customer.name} berhasil didaftarkan dengan ID {customer.customer_id}!')
            # PRG Pattern - redirect after POST
            return redirect('orders:pelanggan-operasional')
        else:
            messages.error(request, 'Gagal mendaftarkan customer. Periksa form kembali.')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Daftar Pelanggan',
    }
    
    return render(request, 'orders/customer_form.html', context)


@login_required
@check_view_permission
def customer_toggle_status(request, pk):
    """Toggle customer status (soft delete)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    customer = get_object_or_404(Customer, pk=pk)
    
    # Check if customer has unpaid invoices
    has_unpaid = Order.objects.filter(
        customer=customer,
        payment_status__in=[PaymentStatus.UNPAID, PaymentStatus.IN_CHECKING]
    ).exists()
    
    warning_message = ""
    if has_unpaid and customer.status == CustomerStatus.ACTIVE:
        warning_message = "Customer ini masih memiliki tunggakan pembayaran!"
        # Log warning (optional - could use Django logging)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Customer {customer.customer_id} - {customer.name} dinonaktifkan dengan tunggakan")
    
    # Toggle status
    if customer.status == CustomerStatus.ACTIVE:
        customer.status = CustomerStatus.INACTIVE
        action = 'dinonaktifkan'
    else:
        customer.status = CustomerStatus.ACTIVE
        action = 'diaktifkan'
    
    customer.save()
    
    message = f'Customer {customer.name} berhasil {action}.'
    if warning_message:
        message += f' {warning_message}'
    
    messages.success(request, message)
    
    return redirect('orders:pelanggan-operasional')

