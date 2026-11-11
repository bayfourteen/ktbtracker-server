from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from apps.users.forms import KTBAuthenticationForm
from apps.users.models import User


class AccountsLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = KTBAuthenticationForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next_url")
        context["error"] = None
        context["page_background"] = "bg-primary"

        return context


class AccountsUserListView(ListView):
    template_name = "accounts/index.html"
    context_object_name = "users"
    model = User

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("first_name", "last_name", "username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_user"] = self.request.GET.get("user")
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            self.template_name = "accounts/widgets/selector.html#user-selector"

        return super().render_to_response(context, **response_kwargs)
