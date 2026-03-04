from django.urls import path
from django.views.generic import TemplateView

app_name = 'main'

urlpatterns = [
    path('', TemplateView.as_view(template_name='layout_app.html'), name='index'),
    path('opname/', TemplateView.as_view(template_name='layout_app.html'), name='opname')
]