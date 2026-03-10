from django.urls import path
from django.views.generic import TemplateView

app_name = 'analytics'

urlpatterns = [
    path('harga-jual/', TemplateView.as_view(template_name='layout_app.html'), name='harga-jual'),
]
