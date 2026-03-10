import re
from datetime import date
from django import forms
from .models import RawMaterial, Supplier, Purchase, PurchaseItem, ProductVariant, ProductType

# ─────────────────────────────────────────────────────────────
# UI Styling Constants (Tailwind CSS)
# ─────────────────────────────────────────────────────────────

SELECT_CLASS = (
    'w-full border border-gray-300 rounded-lg px-4 py-3 pr-10 text-sm text-gray-700 '
    'focus:outline-none focus:ring-2 focus:ring-[#2B308B] appearance-none bg-white cursor-pointer'
)

INPUT_CLASS = (
    'w-full border border-gray-300 rounded-lg px-4 py-3 text-sm text-gray-700 '
    'focus:outline-none focus:ring-2 focus:ring-[#2B308B]'
)

DATE_CLASS = (
    'w-full border border-gray-300 rounded-lg px-4 py-3 text-sm text-gray-700 '
    'focus:outline-none focus:ring-2 focus:ring-[#2B308B]'
)

# ─────────────────────────────────────────────────────────────
# Supplier Management (Administrative)
# ─────────────────────────────────────────────────────────────

class SupplierForm(forms.ModelForm):
    """Form to create or update Supplier profiles."""
    
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'ex: 8XXXXXXXXX (digit only)',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'ex: JL. Raya No. 123',
            'maxlength': 200
        })
    )

    class Meta:
        model = Supplier
        fields = ['name', 'phone_number', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'ex: CV Maju Jaya',
                'maxlength': 50
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Nama supplier tidak boleh kosong.')
        return name

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not re.match(r'^\d{8,15}$', phone):
            raise forms.ValidationError('Nomor telepon harus 8-15 digit angka.')
        return phone


# ─────────────────────────────────────────────────────────────
# Inventory & Production (Operational)
# ─────────────────────────────────────────────────────────────

class RawMaterialInboundForm(forms.Form):
    """Form for recording incoming raw materials (Purchases)."""
    
    receive_date = forms.DateField(
        label='Tanggal Diterima',
        initial=date.today,
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': DATE_CLASS,
        })
    )

    raw_material = forms.ModelChoiceField(
        queryset=RawMaterial.objects.all(),
        label='Jenis Bahan Baku',
        empty_label='-- Pilih bahan baku --',
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )

    quantity = forms.IntegerField(
        label='Jumlah',
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'ex: 2000',
        })
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        label='Nama Supplier',
        empty_label='-- Pilih supplier --',
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )

    def clean(self):
        cleaned_data = super().clean()
        
        # Check if any field is filled (useful if used within a formset)
        has_data = any([
            cleaned_data.get('receive_date'),
            cleaned_data.get('raw_material'),
            cleaned_data.get('quantity'),
            cleaned_data.get('supplier'),
        ])
        
        # If some data is present, validate all required fields
        if has_data:
            if not cleaned_data.get('receive_date'):
                self.add_error('receive_date', 'Tanggal Diterima wajib diisi.')
            if not cleaned_data.get('raw_material'):
                self.add_error('raw_material', 'Jenis Bahan Baku wajib dipilih.')
            if not cleaned_data.get('quantity'):
                self.add_error('quantity', 'Jumlah wajib diisi.')
            elif cleaned_data.get('quantity') <= 0:
                self.add_error('quantity', 'Jumlah harus lebih dari 0.')
            if not cleaned_data.get('supplier'):
                self.add_error('supplier', 'Nama Supplier wajib dipilih.')
        
        return cleaned_data


# ─────────────────────────────────────────────────────────────
# Daily Production
# ─────────────────────────────────────────────────────────────

PRODUCT_TYPE_CHOICES = [
    ('', '-- Pilih tipe garam --'),
    (ProductType.SOFT, 'Garam Halus'),
    (ProductType.HARD, 'Garam Kasar'),
]

class DailyProductionItemForm(forms.Form):
    """Form for recording daily finished goods production."""

    product_type = forms.ChoiceField(
        choices=PRODUCT_TYPE_CHOICES,
        label='Tipe Garam',
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
    )

    product_variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.all(),
        label='Varian/SKU Produk (gram)',
        empty_label='-- Pilih varian --',
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
    )

    quantity = forms.IntegerField(
        label='Jumlah',
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'ex: 2000',
        }),
    )

    production_date = forms.DateField(
        label='Tanggal Produksi',
        initial=date.today,
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': DATE_CLASS,
        }),
    )

    def clean(self):
        cleaned_data = super().clean()

        has_data = any([
            cleaned_data.get('product_type'),
            cleaned_data.get('product_variant'),
            cleaned_data.get('quantity'),
        ])

        if has_data:
            if not cleaned_data.get('product_type'):
                self.add_error('product_type', 'Tipe Garam wajib dipilih.')
            if not cleaned_data.get('product_variant'):
                self.add_error('product_variant', 'Varian/SKU wajib dipilih.')
            else:
                variant = cleaned_data['product_variant']
                ptype = cleaned_data.get('product_type')
                if ptype and variant.product_type != ptype:
                    self.add_error('product_variant', 'Varian tidak sesuai dengan tipe garam yang dipilih.')
            
            if not cleaned_data.get('quantity'):
                self.add_error('quantity', 'Jumlah wajib diisi.')
            elif cleaned_data['quantity'] <= 0:
                self.add_error('quantity', 'Jumlah harus lebih dari 0.')

        return cleaned_data