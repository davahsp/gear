from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views.generic import View, TemplateView, UpdateView, DeleteView, DetailView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.db.models.functions import Concat
from django.db.models import Value

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

class AccountIndexView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):

    permission_required = 'accounts.view_account'

    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
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

class AccountPasswordChangeView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):

    permission_required = 'accounts.changepassword_account'
    
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

class HtmxAccountTableView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'accounts.view_account'
    template_name = 'accounts/htmx/account-table.html'
    model = Account
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        )

        role = self.request.GET.get('role')

        if role:
            if role.lower() == 'owner':
                queryset = queryset.filter(is_superuser=True)
            else:
                queryset = queryset.filter(groups__name=role)

        status = self.request.GET.get('status')

        if status:
            is_active = (status.lower() == 'active')
            queryset = queryset.filter(is_active=is_active)

        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(full_name__icontains=name.strip())

        return queryset

class HtmxToggleStatusView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, View):

    model = Account
    http_method_names = ['post']

    permission_required = 'accounts.togglestatus_account'
    
    # not part of mixin but rather self-defined
    template_name = 'accounts/htmx/account-table-row.html'

    context_object_name = 'a'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.is_active = not self.object.is_active

        self.object.save()

        return render(request, self.template_name, self.get_context_data())