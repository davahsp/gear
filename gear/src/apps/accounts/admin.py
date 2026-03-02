from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import GEARUserCreationForm, GEARUserChangeForm
from .models import GEARUser

class GEARUserAdmin(UserAdmin):
    add_form = GEARUserCreationForm
    form = GEARUserChangeForm
    model = GEARUser

    list_display = [
        'username',
        'phone_number',
        'is_staff',
        'is_active',
    ]

admin.site.register(GEARUserAdmin, GEARUser)
    
