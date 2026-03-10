from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
from django.forms import ValidationError
from django.utils.translation import gettext as _
import re

from .managers import AccountManager

from uuid import uuid4

class Account(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, error_messages={
        'unique': 'Nomor telepon sudah terdaftar dalam sistem',
    }, validators=[
        MinLengthValidator(limit_value=10, message='Nomor telepon minimal terdiri dari 10 angka'),
        RegexValidator(r'^[0-9]+$', message='Nomor telepon hanya boleh memuat angka, tanpa spasi, dash (-), ataupun tambah (+)'),
    ])
    username = None
    address = models.CharField(max_length=127, blank=True)

    # no modification of db level constraints from the parent class
    # only add validators
    first_name = models.CharField(max_length=150, blank=True, validators=[
        RegexValidator(r'^[A-Za-z ]+$', message='Nama depan hanya boleh terdiri dari huruf alfabet dan spasi'),
    ])
    last_name = models.CharField(max_length=150, blank=True, validators=[
        RegexValidator(r'^[A-Za-z ]+$', message='Nama belakang hanya boleh terdiri dari huruf alfabet dan spasi'),
    ])

    USERNAME_FIELD = 'phone_number'

    objects = AccountManager()

    def get_upload_target(instance, filename: str):
        return f'avatars/avatar-{instance.id}/{filename}'

    # avatar file uploaded to /MEDIA_ROOT/avatars/
    avatar = models.ImageField(null=True, upload_to=get_upload_target)

    # override method clean to do custom validation
    def clean(self):

        super().clean()
        
        self.first_name = Account.normalize_name(self.first_name)

        if len(self.first_name) < 3:
            raise ValidationError({'first_name': _('Nama depan harus terdiri dari minimal 3 huruf')})
        
        self.last_name = Account.normalize_name(self.last_name)

        self.address = Account.rm_excess_whitespace(self.address)

    def normalize_name(name: str) -> str:
        name = Account.rm_excess_whitespace(name)
        name = ' '.join([n.capitalize() for n in name.split(' ')])
        return name
    
    def rm_excess_whitespace(text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    # override method clean to do custom validation
    def clean(self):

        super().clean()
        
        self.first_name = Account.normalize_name(self.first_name)

        if len(self.first_name) < 3:
            raise ValidationError({'first_name': _('Nama depan harus terdiri dari minimal 3 huruf')})
        
        self.last_name = Account.normalize_name(self.last_name)

        self.address = Account.rm_excess_whitespace(self.address)

    def normalize_name(name: str) -> str:
        name = Account.rm_excess_whitespace(name)
        name = ' '.join([n.capitalize() for n in name.split(' ')])
        return name
    
    def rm_excess_whitespace(text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def __str__(self):
        return self.get_full_name()
    
    class Meta:

        permissions = [
            ('togglestatus_account', 'Can activate and deactivate account'),
            ('changepassword_account', 'Can change account password'),
        ]