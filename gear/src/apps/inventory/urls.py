from django.urls import path
from django.views.generic import TemplateView
from .views import SupplierListView, SupplierCreateView, SupplierUpdateView

app_name = 'inventory'

urlpatterns = [
    path('bahan-baku/', TemplateView.as_view(template_name='layout_app.html'), name='bahan-baku'),
    path('barang-jadi/', TemplateView.as_view(template_name='layout_app.html'), name='barang-jadi'),
    path('inventori-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='inventori-analitik'),
    
    path('suppliers/', SupplierListView.as_view(), name='supplier'),
    path('suppliers/add/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<str:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_update'),
]