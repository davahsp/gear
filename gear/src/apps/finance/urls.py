from django.urls import path
from django.views.generic import TemplateView

app_name = 'finance'

urlpatterns = [
    path('keuangan-operasional/', TemplateView.as_view(template_name='base.html'), name='keuangan-operasional'),
    path('keuangan-analitik/', TemplateView.as_view(template_name='base.html'), name='keuangan-analitik'),
]
