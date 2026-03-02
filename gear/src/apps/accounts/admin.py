from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import GEARUserCreationForm, GEARUserChangeForm
from .models import GEARUser

class GEARUserAdmin(UserAdmin):
    add_form = GEARUserCreationForm
    form = GEARUserChangeForm
    model = GEARUser

    ordering = 'first_name', 'last_name'

    list_display = [
        'first_name',
        'phone_number',
        'is_staff',
        'is_active',
    ]

    # add user page fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password', 'first_name', 'is_active', 'is_staff'),
        }),
    )

    # edit user page fields
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(GEARUser, GEARUserAdmin)
    
