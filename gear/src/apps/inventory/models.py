from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from datetime import date
import re

AUTH_USER_MODEL = get_user_model()

class ProductType(models.TextChoices):

    SOFT = 'SOFT', 'Soft'
    HARD = 'HARD', 'Hard'

class ProductVariant(models.Model):
    
    product_type = models.CharField(max_length=7, choices=ProductType.choices)
    size_grams = models.IntegerField(validators=[MinValueValidator(1)])
    qty_in_stock = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return str(self.size_grams)

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

    def __str__(self):
        return self.name

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

    id = models.CharField(
        max_length=10,
        primary_key=True,
        editable=False
    )
    name = models.CharField(
        max_length=63,
        unique=True,
        error_messages={
            'unique': 'Nama supplier sudah terdaftar di sistem.'
        }
    )
    email = models.EmailField(max_length=31, null=True)
    phone_number = models.CharField(max_length=15,  null=True)
    address = models.CharField(max_length=127, null=True)
    last_transaction = models.DateField(null=True)

    def __str__(self):
        return self.name

    # Menambahkan field is_active untuk menandai apakah supplier masih aktif atau tidak
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-generate ID dengan format SUP-XXXX saat create (tanpa menyimpan)."""
        if not self.id:
            # Hitung supplier berikutnya
            last_supplier = Supplier.objects.all().order_by('-id').first()
            if last_supplier:
                # Extract angka dari ID terakhir (mis: "SUP-0042" -> 42)
                try:
                    last_num = int(last_supplier.id.split('-')[1])
                    next_num = last_num + 1
                except (IndexError, ValueError):
                    next_num = 1
            else:
                next_num = 1
            
            self.id = f"SUP-{next_num:04d}"
        
        super().save(*args, **kwargs)

    @property
    def whatsapp_number(self):
        """Normalisasi nomor supplier ke format WhatsApp ID: 62xxxxxxxxxx."""
        if not self.phone_number:
            return ''

        digits = re.sub(r'\D', '', self.phone_number)
        if not digits:
            return ''

        if digits.startswith('0'):
            return f"62{digits[1:]}"

        if digits.startswith('62'):
            return digits

        return f"62{digits}"

    @property
    def whatsapp_url(self):
        """URL WhatsApp API siap pakai untuk nomor supplier."""
        normalized_number = self.whatsapp_number
        if not normalized_number:
            return ''
        return f"https://wa.me/{normalized_number}"

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

    is_active = models.BooleanField(default=True)

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


