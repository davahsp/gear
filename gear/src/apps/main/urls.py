from django.urls import path
from django.views.generic import RedirectView, TemplateView
from django.urls import reverse_lazy

app_name = 'main'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('accounts:my-account')), name='index'),
    path('opname/', TemplateView.as_view(template_name='layout_app.html'), name='opname'),
]