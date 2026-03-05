from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, FormView, UpdateView
from django.urls import reverse_lazy
from django.conf import settings

from .forms import GEARUserCreateForm, GEARUserUpdateForm, PhoneAuthenticationForm
from .models import GEARUser

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):

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

class CreateAccountView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    
    permission_required = 'accounts.add_gearuser'

    template_name = 'accounts/create.html'
    form_class = GEARUserCreateForm
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

    def form_valid(self, form: GEARUserCreateForm):
        user = form.save(commit=False)
        user.set_password(settings.USER_DEFAULT_PASSWORD)
        user.save()
        form.save_m2m()

        return super().form_valid(form)

class PhoneLoginView(LoginView):

    template_name = 'accounts/login.html'
    authentication_form = PhoneAuthenticationForm
    redirect_authenticated_user = True

class UpdateAccountView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'accounts.edit_gearuser'
    form_class = GEARUserUpdateForm
    template_name = 'accounts/my-account-update.html'
    success_url = reverse_lazy('accounts:my-account')

    def get_object(self, queryset=None):
        return self.request.user


