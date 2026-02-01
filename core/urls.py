from django.contrib.auth.views import LogoutView
from django.urls import path

from core.views import AccountsLoginView
from tracking import views
from tracking.views import TrackingFormView

app_name = "core"

urlpatterns = [
    path("login/", AccountsLoginView.as_view(), name="accounts-login"),
    path("logout/", LogoutView.as_view(), name="accounts-logout"),
]
