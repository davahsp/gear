from django import forms
from .models import Supplier
import re

class SupplierForm(forms.ModelForm):
    """Form input supplier dengan styling UI dan validasi field tambahan.

    Catatan:
    - `name` dibatasi maksimum 50 karakter.
    - `phone_number` opsional, tetapi jika diisi harus 8-15 digit angka.
    - `address` opsional, maksimum 200 karakter.
    """

    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-800',
            'placeholder': 'ex: 8XXXXXXXXX (otomatis ditambah +62)',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-800',
            'placeholder': 'ex: JL XXXXX',
            'maxlength': 200
        })
    )
    class Meta:
        """Konfigurasi field model yang diekspos ke form."""
        model = Supplier
        fields = ['name', 'phone_number', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-800',
                'placeholder': 'ex: CV XXXX',
                'maxlength': 50
            }),
        }

    def clean_name(self):
        """Validasi panjang nama supplier."""
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Nama supplier tidak boleh kosong.')
        if len(name) > 50:
            raise forms.ValidationError('Nama supplier maksimal 50 karakter.')
        return name

    def clean_phone_number(self):
        """Validasi nomor telepon agar hanya digit dengan panjang 8-15."""
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone:
            if not re.match(r'^\d{8,15}$', phone):
                raise forms.ValidationError('Nomor telepon harus 8-15 digit angka tanpa simbol atau spasi.')
        return phone

    def clean_address(self):
        """Validasi batas maksimal panjang alamat."""
        address = self.cleaned_data.get('address', '').strip()
        if address and len(address) > 200:
            raise forms.ValidationError('Alamat maksimal 200 karakter.')
        return address
