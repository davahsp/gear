from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from datetime import date

AUTH_USER_MODEL = get_user_model()

class OrderStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', 'Mengajukan'
    CONFIRMED = 'IN_PROGRESS', 'Diproses'
    IN_SHIPPING = 'IN_SHIPPING', 'Diantar'
    DELIVERED = 'DELIVERED', 'Diterima'
    COMPLETED = 'COMPLETED', 'Selesai'
    CANCELLED = 'CANCELLED', 'Dibatalkan'

class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Cash'
    ACCOUNT = 'ACCOUNT', 'Account'

class PaymentStatus(models.TextChoices):
    UNINITIATED = 'UNINITIATED', 'Uninitiated'
    UNPAID = 'UNPAID', 'Unpaid',
    IN_CHECKING = 'IN_CHECKING', 'In Checking'
    PAID = 'PAID', 'Paid'

class CustomerStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Aktif'
    INACTIVE = 'INACTIVE', 'Non Aktif'

class CustomerSegment(models.TextChoices):
    NEW = 'NEW', 'New Customer'
    REGULAR = 'REGULAR', 'Regular'
    VIP = 'VIP', 'VIP'

class Order(models.Model):

    order_number = models.CharField(max_length=20, unique=True, blank=True, db_index=True)
    order_status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.REQUESTED)
    total_price = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    order_date = models.DateField(default=date.today)
    date_delivered = models.DateField(null=True, blank=True)

    payment_method = models.CharField(max_length=7, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=15, choices=PaymentStatus.choices, default=PaymentStatus.UNINITIATED)

    payment_due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)

    is_troubled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    who_inputs = models.ForeignKey(to=AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='order_inputs')
    
    customer = models.ForeignKey(to='Customer',
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='orders')

    class Meta:
        ordering = ['-order_date', '-id']

    def __str__(self):
        return self.order_number or f'Order #{self.pk}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_number:
            year_month = self.order_date.strftime('%Y%m')
            self.order_number = f'ORD-{year_month}-{self.pk:08d}'
            Order.objects.filter(pk=self.pk).update(order_number=self.order_number)

class OrderItem(models.Model):

    order = models.ForeignKey(to='Order', 
                              on_delete=models.CASCADE,
                              related_name='items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    subtotal = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    # lazy relation
    product_variant = models.ForeignKey(to='inventory.ProductVariant',
                                        on_delete=models.PROTECT,
                                        related_name='order_items')
    
    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['order', 'product_variant'],
                name='order cannot have duplicate order items with the same variant'
            ),
        ]

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class OrderChangeType(models.TextChoices):
    CREATED = 'CREATED', 'Dibuat'
    UPDATED = 'UPDATED', 'Diperbarui'
    STATUS_CHANGED = 'STATUS_CHANGED', 'Status Diubah'
    CANCELLED = 'CANCELLED', 'Dibatalkan'


class OrderHistory(models.Model):
    order = models.ForeignKey(to='Order',
                              on_delete=models.CASCADE,
                              related_name='history')
    changed_by = models.ForeignKey(to=AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='order_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(max_length=20, choices=OrderChangeType.choices)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.order.order_number} - {self.get_change_type_display()} oleh {self.changed_by} pada {self.changed_at}'

class Customer(models.Model):
    
    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=63, unique=True, verbose_name="Nama Toko/Customer")
    email = models.EmailField(max_length=31, null=True, blank=True)
    phone_number = models.CharField(max_length=15, verbose_name="No HP")
    address = models.CharField(max_length=127, null=True, blank=True, verbose_name="Alamat")
    
    status = models.CharField(max_length=10, choices=CustomerStatus.choices, default=CustomerStatus.ACTIVE)
    segment = models.CharField(max_length=10, choices=CustomerSegment.choices, default=CustomerSegment.NEW)
    total_transactions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    last_transaction = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    sales_pic = models.ForeignKey(
        to=AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='customers',
        verbose_name="Sales PIC"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Generate customer ID: CUST-YYYYMM-XXXX
            from datetime import datetime
            year_month = datetime.now().strftime('%Y%m')
            
            # Get last customer ID for this month
            last_customer = Customer.objects.filter(
                customer_id__startswith=f'CUS-{year_month}'
            ).order_by('customer_id').last()
            
            if last_customer:
                last_num = int(last_customer.customer_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.customer_id = f'CUS-{year_month}-{new_num:04d}'
        
        super().save(*args, **kwargs)
    
    @property
    def has_unpaid_invoices(self):
        """Check if customer has any unpaid or in-checking invoices"""
        return Order.objects.filter(
            customer=self,
            payment_status__in=[PaymentStatus.UNPAID, PaymentStatus.IN_CHECKING]
        ).exists()