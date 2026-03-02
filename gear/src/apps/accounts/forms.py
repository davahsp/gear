from .models import GEARUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class GEARUserCreationForm(UserCreationForm):
    
    class Meta:
        model = GEARUser,
        fields = ('username', 'phone_number')

class GEARUserChangeForm(UserChangeForm):
    
    class Meta:
        model = GEARUser,
        fields = ('username', 'phone_number')