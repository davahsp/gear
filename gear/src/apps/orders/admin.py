from django.contrib import admin
from .models import Order, OrderItem, Customer, OrderHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_date', 'customer', 'who_inputs', 'order_status', 'total_price')
    list_filter = ('order_status', 'payment_method', 'order_date')
    search_fields = ('order_number', 'customer__name')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'updated_at')


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'change_type', 'changed_by', 'changed_at')
    list_filter = ('change_type',)
    readonly_fields = ('order', 'changed_by', 'changed_at', 'change_type', 'old_values', 'new_values', 'notes')


admin.site.register([OrderItem, Customer])
