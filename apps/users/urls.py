from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import AccountsLoginView, AccountsUserListView

app_name = "users"

urlpatterns = [
    # - - - Home Page - - -
    path("", AccountsUserListView.as_view(), name="index"),
    path("login/", AccountsLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
