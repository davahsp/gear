from django.urls import path
from django.views.generic import TemplateView

app_name = 'inventory'

urlpatterns = [
    path('bahan-baku/', TemplateView.as_view(template_name='layout_app.html'), name='bahan-baku'),
    path('barang-jadi/', TemplateView.as_view(template_name='layout_app.html'), name='barang-jadi'),
    path('supplier/', TemplateView.as_view(template_name='layout_app.html'), name='supplier'),
    path('inventori-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='inventori-analitik'),
]