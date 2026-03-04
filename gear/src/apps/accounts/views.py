from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy

from .forms import UserForm, PhoneAuthenticationForm
from .models import GEARUser

class IndexView(LoginRequiredMixin, TemplateView):

    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sales = GEARUser.objects.filter(groups__name='Sales')
        warehouse = GEARUser.objects.filter(groups__name='Warehouse')
        finance = GEARUser.objects.filter(groups__name='Finance')

        context['sales'] = sales
        context['warehouse'] = warehouse
        context['finance'] = finance

        return context

class CreateAccountView(LoginRequiredMixin, FormView):

    template_name = 'accounts/create.html'
    form_class = UserForm
    success_url = reverse_lazy('accounts:index')

    def get_initial(self):
        initial = super().get_initial()
        role_name = self.request.GET.get('default_role')

        if role_name:
            try:
                group = Group.objects.get(name__iexact=role_name.lower())
                initial['groups'] = [group.id]
            except Group.DoesNotExist:
                pass

        return initial

    def form_valid(self, form: UserForm):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form: UserForm):
        return super().form_invalid(form)

class PhoneLoginView(LoginView):

    template_name = 'accounts/login.html'
    authentication_form = PhoneAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)