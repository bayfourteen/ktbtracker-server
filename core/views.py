from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render

from core.forms import AccountsLoginForm


# Create your views here.

class AccountsLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = AccountsLoginForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next_url")
        context["error"] = None
        context["page_background"] = "bg-primary"

        return context
