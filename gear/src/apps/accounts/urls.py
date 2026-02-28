from django.urls import path
from django.views.generic import TemplateView

app_name = 'accounts'

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='index'),
    path('my-account/', TemplateView.as_view(template_name='base.html'), name='my-account'),
]
