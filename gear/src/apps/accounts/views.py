from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.conf import settings

from .forms import AccountCreateForm, AccountUpdateForm, PhoneAuthenticationForm
from .models import GEARUser

class PhoneLoginView(LoginView):

    template_name = 'accounts/login.html'
    authentication_form = PhoneAuthenticationForm
    redirect_authenticated_user = True

class MyAccountDetailView(LoginRequiredMixin, DetailView):

    template_name = 'accounts/my-account.html'

    # override get_object to directly get the user object from request, 
    # bypassing the fetch from user object manager and filter with pk in kwargs (which the caller won't provide)
    def get_object(self, queryset=None):
        return self.request.user

class MyAccountUpdateView(LoginRequiredMixin, UpdateView):
    form_class = AccountUpdateForm
    template_name = 'accounts/my-account-update.html'
    success_url = reverse_lazy('accounts:my-account')

    def get_object(self, queryset=None):
        return self.request.user

class IndexView(LoginRequiredMixin, TemplateView):

    permission_required = 'accounts.view_gearuser'

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
    
class AccountCreateView(LoginRequiredMixin, CreateView):
    
    template_name = 'accounts/create.html'
    form_class = AccountCreateForm
    success_url = reverse_lazy('accounts:index')

    def get_initial(self):
        initial = super().get_initial()
        role_name = self.request.GET.get('default_role')

        if role_name:
            try:
                group = Group.objects.get(name__iexact=role_name)
                initial['groups'] = [group.id]
            except Group.DoesNotExist:
                pass

        return initial
    
    def form_valid(self, form: AccountCreateForm):

        # set the user password to default password defined in env
        form.instance.set_password(settings.USER_DEFAULT_PASSWORD)
        return super().form_valid(form)
    
class AccountDetailView(LoginRequiredMixin, DetailView):

    model = GEARUser
    template_name = 'accounts/detail.html'

class AccountUpdateView(LoginRequiredMixin, UpdateView):

    form_class = AccountUpdateForm
    template_name = 'accounts/update.html'

    success_url = reverse_lazy('accounts:index')

    model = GEARUser
    
class AccountDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('accounts:index')
    template_name = 'accounts/delete.html'
    model = GEARUser



