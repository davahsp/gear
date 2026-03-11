from .models import Account
from django.contrib.auth.forms import (
    UserCreationForm, 
    UserChangeForm, 
    AuthenticationForm, 
    PasswordChangeForm, 
    SetPasswordForm,
    PasswordResetForm,
)
from django.contrib.auth.models import Group
from django.forms import ModelForm
from django import forms
from django.conf import settings

class AccountCreationForm(UserCreationForm):
    
    class Meta:
        model = Account
        fields = ('first_name', 'phone_number')

class AccountChangeForm(UserChangeForm):
    
    class Meta:
        model = Account
        fields = ('first_name', 'phone_number')

class AccountCreateForm(ModelForm):

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer'
        }),
        required=True
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'groups']
        labels = {
            'groups': 'Role',
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'phone_number': 'Kontak',
            'address': 'Alamat',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'Masukkan nama depan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'Masukkan nama belakang'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'ex: 08XXXXXXXXXX'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'ex: Jl. XXXXX'
            }),
        }
    
    def save(self, commit=True):
        self.instance.set_password(settings.USER_DEFAULT_PASSWORD)
        return super().save(commit)

class AccountUpdateForm(ModelForm):
    
    class Meta:
        model = Account
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'address',
            'avatar'
        ]
        labels = {
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'phone_number': 'Kontak',
            'email': 'Email',
            'address': 'Alamat',
            'avatar': 'Avatar',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'Masukkan nama depan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'Masukkan nama belakang'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'ex: 08XXXXXXXXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'ex: nama@email.com'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
                'placeholder': 'ex: Jl. XXXXX'
            }),
            'avatar': forms.FileInput(attrs={
                # Uses Tailwind's `file:` modifier to style the browse button inside the input
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer',
            }),
        }

class AccountPasswordChangeForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].label = 'Password Baru'
        self.fields['new_password2'].label = 'Konfirmasi Password Baru'

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none mt-2',
                'placeholder': f'Masukkan {field.label.lower()}'
            })

class MyAccountPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Override the labels
        self.fields['old_password'].label = 'Password Lama'
        self.fields['new_password1'].label = 'Password Baru'
        self.fields['new_password2'].label = 'Konfirmasi Password Baru'

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none mt-2',
                'placeholder': f'Masukkan {field.label.lower()}'
            })

class PhoneAuthenticationForm(AuthenticationForm):
    base_style = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all'

    username = forms.CharField(
        label='Nomor Telepon',
        widget=forms.TextInput(attrs={
            'class': base_style,
            'placeholder': '08XXXXXX',
            'type': 'tel'
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': base_style,
            'placeholder': '••••••••'
        })
    )

class AccountPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition-all text-gray-900',
            'placeholder': 'Masukkan email terdaftar',
            'autocomplete': 'email'
        })
    )