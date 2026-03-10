from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from .models import Customer, Order, OrderItem, CustomerStatus, PaymentMethod, OrderStatus

User = get_user_model()


class OrderForm(forms.ModelForm):
    """Form untuk membuat dan mengedit Order"""

    class Meta:
        model = Order
        fields = ['customer', 'order_date', 'payment_method']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control',
                'id': 'customer-select',
            }),
            'order_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'customer': 'Pelanggan',
            'order_date': 'Tanggal Order',
            'payment_method': 'Metode Pembayaran',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(
            status=CustomerStatus.ACTIVE
        ).order_by('name')
        self.fields['customer'].empty_label = '-- Pilih Pelanggan --'

    def clean_customer(self):
        customer = self.cleaned_data.get('customer')
        if not customer:
            raise ValidationError('Pelanggan harus dipilih.')
        if customer.status != CustomerStatus.ACTIVE:
            raise ValidationError('Pelanggan tidak aktif.')
        return customer


class OrderItemForm(forms.ModelForm):
    """Form untuk item dalam order (digunakan dalam formset)"""

    class Meta:
        model = OrderItem
        fields = ['product_variant', 'quantity', 'unit_price']
        widgets = {
            'product_variant': forms.Select(attrs={
                'class': 'form-control item-variant',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control item-qty',
                'min': '1',
                'value': '1',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control item-price',
                'min': '0',
            }),
        }
        labels = {
            'product_variant': 'Produk (SKU)',
            'quantity': 'Jumlah',
            'unit_price': 'Harga Satuan',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.inventory.models import ProductVariant
        self.fields['product_variant'].queryset = ProductVariant.objects.all().order_by(
            'product_type', 'size_grams'
        )
        self.fields['product_variant'].empty_label = '-- Pilih Produk --'

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 1:
            raise ValidationError('Jumlah harus minimal 1.')
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is not None and unit_price < 0:
            raise ValidationError('Harga satuan tidak boleh negatif.')
        return unit_price


class BaseOrderItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        variants_seen = set()
        has_valid_items = False

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                variant = form.cleaned_data.get('product_variant')
                quantity = form.cleaned_data.get('quantity')

                if variant and quantity:
                    has_valid_items = True

                    if variant.pk in variants_seen:
                        raise ValidationError('Tidak boleh ada produk duplikat dalam satu pesanan.')
                    variants_seen.add(variant.pk)

                    if quantity > variant.available_stock:
                        raise ValidationError(
                            f'Stok tidak mencukupi untuk {variant}. '
                            f'Tersedia: {variant.available_stock}, Diminta: {quantity}'
                        )

        if not has_valid_items:
            raise ValidationError('Pesanan harus memiliki minimal 1 item.')


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class CustomerForm(forms.ModelForm):
    """Form untuk membuat dan mengedit Customer"""
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'address', 'sales_pic']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Didi Wahyudi',
                'maxlength': '50'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': False
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: 08XXXXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'ex: Jl. XXXXX',
                'rows': 3,
                'maxlength': '200'
            }),
            'sales_pic': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Nama Pelanggan',
            'email': 'Email',
            'phone_number': 'Kontak',
            'address': 'Alamat',
            'sales_pic': 'Sales PIC'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active users in dropdown
        self.fields['sales_pic'].queryset = User.objects.filter(
            is_active=True
        ).order_by('email')
        self.fields['sales_pic'].label_from_instance = lambda obj: obj.get_full_name() or obj.email or obj.phone_number
    
    def clean_phone_number(self):
        """Validasi No HP tidak boleh duplikat"""
        phone_number = self.cleaned_data.get('phone_number')
        
        # Check if phone number already exists (exclude current instance if editing)
        queryset = Customer.objects.filter(phone_number=phone_number)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('Nomor HP sudah terdaftar untuk customer lain.')
        
        return phone_number
    
    def clean_sales_pic(self):
        """Validasi Sales PIC harus aktif"""
        sales_pic = self.cleaned_data.get('sales_pic')
        
        if sales_pic and not sales_pic.is_active:
            raise ValidationError('Sales PIC yang dipilih tidak aktif.')
        
        return sales_pic