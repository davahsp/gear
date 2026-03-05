from .models import GEARUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.forms import ModelForm
from django import forms

class GEARUserCreationForm(UserCreationForm):
    
    class Meta:
        model = GEARUser
        fields = ('first_name', 'phone_number')

class GEARUserChangeForm(UserChangeForm):
    
    class Meta:
        model = GEARUser
        fields = ('first_name', 'phone_number')

class UserForm(ModelForm):

    class Meta:
        model = GEARUser
        fields = ['groups', 'first_name', 'last_name', 'phone_number', 'address']
        labels = {
            'groups': 'Role',
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'phone_number': 'Kontak',
            'address': 'Alamat',
        }
        widgets = {
            'groups': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white'
            }),
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