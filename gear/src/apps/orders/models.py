from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from datetime import date

class OrderStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', 'Requested'
    CONFIRMED = 'IN_PROGRESS', 'In Progress'
    IN_SHIPPING = 'IN_SHIPPING', 'In Shipping'
    DELIVERED = 'DELIVERED', 'Delivered'
    COMPLETED = 'COMPLETED', 'Completed'

class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Cash'
    ACCOUNT = 'ACCOUNT', 'Account'

class PaymentStatus(models.TextChoices):
    UNINITIATED = 'UNINITIATED', 'Uninitiated'
    UNPAID = 'UNPAID', 'Unpaid',
    IN_CHECKING = 'IN_CHECKING', 'In Checking'
    PAID = 'PAID', 'Paid'

class Order(models.Model):

    order_status = models.CharField(max_length=15, choices=OrderStatus.choices)
    total_price = models.IntegerField(validators=[MinValueValidator(0)])

    order_date = models.DateField(default=date.today)
    date_delivered = models.DateField(null=True)

    payment_method = models.CharField(max_length=7, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=15, choices=PaymentStatus.choices)

    payment_due_date = models.DateField(null=True)
    payment_date = models.DateField(null=True)

    is_troubled = models.BooleanField(default=False)

    who_inputs = models.ForeignKey(to=User,
                                   on_delete=models.PROTECT,
                                   related_name='order_inputs')
    
    customer = models.ForeignKey(to='Customer',
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='orders')

class OrderItem(models.Model):

    order = models.ForeignKey(to='Order', 
                              on_delete=models.CASCADE,
                              related_name='items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

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

class Customer(models.Model):
    
    name = models.CharField(max_length=63, unique=True)
    email = models.EmailField(max_length=31, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=127, null=True)
    last_transaction = models.DateField(null=True)


    

    