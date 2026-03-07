from django.contrib.auth.views import LogoutView
from django.urls import path

from ktbtracker.views import accounts, TrackingListView, TrackingFormView

app_name = "ktbtracker"

urlpatterns = [
    path("login/", accounts.AccountsLoginView.as_view(), name="accounts-login"),
    path("logout/", LogoutView.as_view(), name="accounts-logout"),
    path("tracking/", TrackingListView.as_view(), name="tracking-list"),
    path("tracking/edit/", TrackingFormView.as_view(), name="tracking-edit"),
]
