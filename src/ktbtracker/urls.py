from django.contrib.auth.views import LogoutView
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from ktbtracker.views import AccountsLoginView, TrackingEditView, TrackingListView
from ktbtracker.api.urls import router as api_router


urlpatterns = [
    # iOS clients send username/password here to receive access + refresh tokens
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # iOS clients send refresh token here to receive a new access token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # -- API v1 Paths --
    path("api/", include(api_router.urls)),
    # -- UI Paths --
    path("accounts/login/", AccountsLoginView.as_view(), name="accounts-login"),
    path("accounts/logout/", LogoutView.as_view(), name="accounts-logout"),
    path("tracking/", TrackingListView.as_view(), name="tracking-list"),
    path(
        "tracking/<date:tracking_date>/editor",
        TrackingEditView.as_view(),
        name="tracking-edit",
    ),
]
