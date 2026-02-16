from django.contrib.auth.views import LogoutView
from django.urls import path

from ktbtracker.views import accounts

app_name = "ktbtracker"

urlpatterns = [
    path("login/", accounts.AccountsLoginView.as_view(), name="accounts-login"),
    path("logout/", LogoutView.as_view(), name="accounts-logout"),
]
