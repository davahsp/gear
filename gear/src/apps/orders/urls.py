from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'orders'

urlpatterns = [
    # Order CRUD (PBI 15-20)
    path('pemesanan-operasional/', views.order_list, name='pemesanan-operasional'),
    path('list/', views.order_list, name='order-list'),
    path('add/', views.order_create, name='order-create'),
    path('<int:pk>/', views.order_detail, name='order-detail'),
    path('<int:pk>/edit/', views.order_edit, name='order-edit'),
    path('<int:pk>/update-status/', views.order_update_status, name='order-update-status'),
    path('<int:pk>/cancel/', views.order_cancel, name='order-cancel'),
    path('api/variant-prices/', views.variant_price_api, name='variant-price-api'),

    # Customer management
    path('pelanggan-operasional/', views.customer_list, name='pelanggan-operasional'),
    path('customers/add/', views.customer_add, name='customer-add'),
    path('customers/<int:pk>/toggle-status/', views.customer_toggle_status, name='customer-toggle-status'),

    # Analytics placeholders
    path('pemesanan-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='pemesanan-analitik'),
    path('performa-sales/', TemplateView.as_view(template_name='layout_app.html'), name='performa-sales'),
    path('pelanggan-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='pelanggan-analitik'),
]