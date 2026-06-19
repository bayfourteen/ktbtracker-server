from django.contrib.auth.views import LogoutView
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from ktbtracker.views import AccountsLoginView, TrackingEditView, TrackingListView
from ktbtracker.api.urls import router as api_router


urlpatterns = [
    #
    # --- Application Programming Interface (API) Paths ---
    #
    # -- JWT Authentication Endpoints --
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # -- Swagger Documentation Endpoints --
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # -- Application API Endpoints --
    path("api/", include(api_router.urls)),
    #
    # --- User Interface (UI) Paths ---
    #
    # -- Accounts (Authentication) Endpoints --
    path("accounts/login/", AccountsLoginView.as_view(), name="accounts-login"),
    path("accounts/logout/", LogoutView.as_view(), name="accounts-logout"),
    # -- Tracking Emdpoints --
    path("tracking/", TrackingListView.as_view(), name="tracking-list"),
    path(
        "tracking/<date:tracking_date>/editor",
        TrackingEditView.as_view(),
        name="tracking-edit",
    ),
]
