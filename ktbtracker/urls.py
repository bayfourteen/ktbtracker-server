from django.contrib.auth.views import LogoutView
from django.urls import path

from ktbtracker.views import accounts, TrackingListView, TrackingFormView, TrackingEditView, TrackingIndexView, TrackingHeaderView

app_name = "ktbtracker"

urlpatterns = [
    path("accounts/login/", accounts.AccountsLoginView.as_view(), name="accounts-login"),
    path("accounts/logout/", LogoutView.as_view(), name="accounts-logout"),
    path("tracking/", TrackingIndexView.as_view(), name="tracking-index"),
    path("tracking/_tracking_list", TrackingListView.as_view(), name="tracking-list"),
    path("tracking/<date:tracking_date>/editor", TrackingEditView.as_view(), name="tracking-edit"),
]
