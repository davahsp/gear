from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy

from .forms import AccountCreateForm, AccountUpdateForm, MyAccountPasswordChangeForm, PhoneAuthenticationForm, AccountPasswordChangeForm
from .models import Account

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
    
class MyAccountPasswordChangeView(PasswordChangeView):

    form_class = MyAccountPasswordChangeForm
    template_name = 'accounts/my-account-password-change.html'
    success_url = reverse_lazy('accounts:my-account')

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):

    permission_required = 'accounts.view_account'
    permission_denied_message = 'You do not have authorization to view all accounts'

    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['accounts'] = Account.objects.all() 
        context['groups'] = Group.objects.all()

        return context
    
class AccountCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = 'accounts.add_account'

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
    
class AccountDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):

    permission_required = 'accounts.view_account'

    model = Account
    template_name = 'accounts/detail.html'

class AccountUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

    permission_required = 'accounts.change_account'

    form_class = AccountUpdateForm
    template_name = 'accounts/update.html'

    success_url = reverse_lazy('accounts:index')

    model = Account

class AccountPasswordChangeView(SingleObjectMixin, FormView):
    
    form_class = AccountPasswordChangeForm
    model = Account

    template_name = 'accounts/account-password-change.html'
    success_url = reverse_lazy('accounts:index')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.object
        return kwargs
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form) 
    
class AccountDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

    permission_required = 'accounts.delete_account'

    success_url = reverse_lazy('accounts:index')
    template_name = 'accounts/delete.html'
    model = Account