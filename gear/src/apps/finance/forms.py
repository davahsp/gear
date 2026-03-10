from django import forms
from .models import FinanceEntry, EntryCategory, EntryType
from django.core.exceptions import ValidationError


class FinanceEntryForm(forms.ModelForm):
    """Form for creating operational cash transactions"""
    
    jenis = forms.ChoiceField(
        choices=EntryType.choices,
        required=False,
        label='Jenis',
        initial='EXPENSE',
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = FinanceEntry
        fields = ['transaction_date', 'category', 'nominal', 'description']
        labels = {
            'transaction_date': 'Tanggal',
            'category': 'Kategori',
            'nominal': 'Nominal',
            'description': 'Keterangan',
        }
        widgets = {
            'transaction_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_category'
            }),
            'nominal': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'ex: 2.000',
                'min': '1',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'ex: Ongkos Kirim ke Lampung',
                'rows': 3,
                'maxlength': '200',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Default jenis to EXPENSE
        if not self.data and not self.instance.pk:
            self.initial['jenis'] = EntryType.EXPENSE
        
        # If this is a bound form (has data), filter categories by jenis
        if self.data:
            try:
                jenis = self.data.get('jenis', EntryType.EXPENSE)
                if jenis:
                    self.fields['category'].queryset = EntryCategory.objects.filter(type=jenis).order_by('name')
            except (ValueError, TypeError):
                pass
        # If instance exists, set correct categories and jenis
        elif self.instance.pk:
            self.fields['category'].queryset = EntryCategory.objects.filter(
                type=self.instance.category.type
            ).order_by('name')
            self.initial['jenis'] = self.instance.category.type
        else:
            # Default to EXPENSE categories
            self.fields['category'].queryset = EntryCategory.objects.filter(type=EntryType.EXPENSE).order_by('name')
    
    def clean_nominal(self):
        """Validate that nominal is greater than 0"""
        nominal = self.cleaned_data.get('nominal')
        if nominal is not None and nominal <= 0:
            raise ValidationError('Nominal harus lebih besar dari 0')
        return nominal
    
    def clean(self):
        """Validate that category matches the selected jenis"""
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        jenis = cleaned_data.get('jenis')
        
        # Default to EXPENSE if not provided
        if not jenis:
            jenis = EntryType.EXPENSE
            cleaned_data['jenis'] = jenis
        
        if category and jenis:
            if category.type != jenis:
                raise ValidationError('Kategori tidak sesuai dengan jenis transaksi')
        
        return cleaned_data
