from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.views import LogoutView

from .views import IndexView, CreateAccountView, PhoneLoginView, UpdateAccountView

app_name = 'accounts'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('create/', CreateAccountView.as_view(), name='create'),
    path('my-account/', TemplateView.as_view(template_name='accounts/my-account.html'), name='my-account'),
    path('my-account/update/', UpdateAccountView.as_view(), name='my-account-update'),
    path('login/', PhoneLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGIN_URL), name='logout'),
]
