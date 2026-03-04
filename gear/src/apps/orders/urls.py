from django.urls import path
from django.views.generic import TemplateView

app_name = 'orders'

urlpatterns = [
    path('pemesanan-operasional/', TemplateView.as_view(template_name='layout_app.html'), name='pemesanan-operasional'),
    path('pelanggan-operasional/', TemplateView.as_view(template_name='layout_app.html'), name='pelanggan-operasional'),
    path('pemesanan-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='pemesanan-analitik'),
    path('performa-sales/', TemplateView.as_view(template_name='layout_app.html'), name='performa-sales'),
    path('pelanggan-analitik/', TemplateView.as_view(template_name='layout_app.html'), name='pelanggan-analitik'),
]   
