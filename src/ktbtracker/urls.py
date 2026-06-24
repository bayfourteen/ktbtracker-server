from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from oauth2_provider import urls as oauth2_provider_urls
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from ktbtracker.api.urls import router as api_router
from ktbtracker.views import AccountsLoginView, TrackingEditView, TrackingListView

urlpatterns = [
    # --                                                 --
    # --- Application Programming Interface (API) Paths ---
    # --                                                 --
    # - - - Django OAuth Toolkit (DOT) Endpoints - - -
    path("api/o/", include(oauth2_provider_urls)),
    # - - - JWT Authentication Endpoints - - -
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # - - - Spectacular (Swagger) Documentation Endpoints - - -
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    #
    # - - - Application API Endpoints - - -
    #
    path("api/", include(api_router.urls)),
    # --                                                 --
    # ---            User Interface (UI) Paths          ---
    # --                                                 --
    # - - - Accounts (Authentication) Endpoints - - -
    path("accounts/login/", AccountsLoginView.as_view(), name="accounts-login"),
    path("accounts/logout/", LogoutView.as_view(), name="accounts-logout"),
    # - - - Tracking Endpoints - - -
    path("tracking/", TrackingListView.as_view(), name="tracking-list"),
    path("tracking/<date:tracking_date>/editor", TrackingEditView.as_view(), name="tracking-edit"),
]
