from django.urls import path
from django.views.generic import TemplateView
from .views import (
    InboundsListView, InboundAddView, InboundDetailView, InboundDeleteView,
    ProductionListView, ProductionAddView,
    SupplierListView, SupplierCreateView, SupplierUpdateView
)

app_name = 'inventory'

urlpatterns = [
    path('inbounds/', InboundsListView.as_view(), name='inbounds'),
    path('inbounds/add/', InboundAddView.as_view(), name='inbound-add'),
    path('inbounds/<int:pk>/', InboundDetailView.as_view(), name='inbound-detail'),
    path('inbounds/<int:pk>/delete/', InboundDeleteView.as_view(), name='inbound-delete'),
    path('production/', ProductionListView.as_view(), name='production'),
    path('production/add/', ProductionAddView.as_view(), name='production-add'),
    path('bahan-baku/', TemplateView.as_view(template_name='layout_app.html'), name='bahan-baku'),
    path('barang-jadi/', TemplateView.as_view(template_name='layout_app.html'), name='barang-jadi'),
    path('inventori-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='inventori-analitik'),
    path('suppliers/', SupplierListView.as_view(), name='supplier'),
    path('suppliers/add/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<str:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_update'),
]