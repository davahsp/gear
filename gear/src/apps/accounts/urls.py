from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.PhoneLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGIN_URL), name='logout'),
    path('my-account/', views.MyAccountDetailView.as_view(), name='my-account'),
    path('my-account/update/', views.MyAccountUpdateView.as_view(), name='my-account-update'),
    path('my-account/password-change/', views.MyAccountPasswordChangeView.as_view(), name='my-account-password-change'),
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.AccountCreateView.as_view(), name='create'),
    path('<pk>/', views.AccountDetailView.as_view(), name='detail'),
    path('<pk>/update/', views.AccountUpdateView.as_view(), name='update'),
    path('<pk>/password-change/', views.AccountPasswordChangeView.as_view(), name='password-change'),
    path('<pk>/delete/', views.AccountDeleteView.as_view(), name='delete'),
]
