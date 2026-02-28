from django.urls import path
from django.views.generic import TemplateView

app_name = 'analytics'

urlpatterns = [
    path('harga-jual/', TemplateView.as_view(template_name='base.html'), name='harga-jual'),
]
