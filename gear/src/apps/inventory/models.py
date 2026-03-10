from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from datetime import date

AUTH_USER_MODEL = get_user_model()

class ProductType(models.TextChoices):

    SOFT = 'SOFT', 'Soft'
    HARD = 'HARD', 'Hard'

class ProductVariant(models.Model):
    
    product_type = models.CharField(max_length=7, choices=ProductType.choices)
    size_grams = models.IntegerField(validators=[MinValueValidator(1)])
    qty_in_stock = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['product_type', 'size_grams'],
                name='unique combination of product_type and size_grams as each variant'
            ),
        ]

class RawMaterial(models.Model):

    name = models.CharField(max_length=31, unique=True)
    unit = models.CharField(max_length=7)
    qty_in_stock = models.IntegerField(validators=[MinValueValidator(0)])
    last_restocked = models.DateField(null=True)

class DailyProduction(models.Model):

    production_date = models.DateField(default=date.today)
    notes = models.TextField(null=True)

    who_inputs = models.ForeignKey(to=AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='daily_production_inputs')

class DailyProductionItem(models.Model):

    daily_production = models.ForeignKey(to='DailyProduction',
                                         on_delete=models.CASCADE,
                                         related_name='items')
    
    product_variant = models.ForeignKey(to='ProductVariant',
                                        on_delete=models.PROTECT,
                                        related_name='daily_production_items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints=[
            models.constraints.UniqueConstraint(
                fields=['daily_production', 'product_variant'],
                name='within a single daily production, there cannot be duplicate variants',
            ),
        ]

class DailyProductionRawItem(models.Model):

    daily_production = models.ForeignKey(to='DailyProduction',
                                         on_delete=models.CASCADE,
                                         related_name='raw_items')
    
    raw_material = models.ForeignKey(to='RawMaterial',
                                     on_delete=models.PROTECT,
                                     related_name='daily_production_raw_items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints=[
            models.constraints.UniqueConstraint(
                fields=['daily_production', 'raw_material'],
                name='within a single daily production, there cannot be duplicate raw materials',
            ),
        ]

class Supplier(models.Model):

    name = models.CharField(max_length=63, unique=True)
    email = models.EmailField(max_length=31, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=127, null=True)
    last_transaction = models.DateField(null=True)

class Purchase(models.Model):

    supplier = models.ForeignKey(to='Supplier',
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='purchases')
    
    total_price = models.IntegerField(validators=[MinValueValidator(0)])

    purchase_date = models.DateField(default=date.today)
    receive_date = models.DateField(default=date.today)

    who_inputs = models.ForeignKey(to=AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='purchase_inputs')

class PurchaseItem(models.Model):

    purchase = models.ForeignKey(to='Purchase',
                                 on_delete=models.CASCADE,
                                 related_name='items')
    
    raw_material = models.ForeignKey(to='RawMaterial',
                                     on_delete=models.PROTECT,
                                     related_name='purchase_items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    # this represents the total price within a purchase item only
    # under almost every circumstances, base price * quantity = subtotal
    subtotal_price = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['purchase', 'raw_material'],
                name='uniqueness of raw_material within a purchase'
            ),
        ]


