from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt

from ktbtracker.forms import KTBAuthenticationForm


class AccountsLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = KTBAuthenticationForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next_url")
        context["error"] = None
        context["page_background"] = "bg-primary"

        return context
