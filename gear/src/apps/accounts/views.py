from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.db import transaction

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

        context['accounts'] = GEARUser.objects.all() 
        context['groups'] = Group.objects.all()

        return context
    
class AccountCreateView(LoginRequiredMixin, CreateView):
    
    template_name = 'accounts/create.html'
    form_class = AccountCreateForm
    success_url = reverse_lazy('accounts:index')

    def get_initial(self):
        initial = super().get_initial()
        group_name = self.request.GET.get('default_role')

        if group_name:
            try:
                group = Group.objects.get(name__iexact=group_name)
                initial['groups'] = [group.id]
            except Group.DoesNotExist:
                pass

        return initial
    
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



