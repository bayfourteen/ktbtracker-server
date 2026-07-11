from django.urls import include, path
from oauth2_provider import urls as oauth2_urls
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from ktbtracker.api.views import (
    CandidateViewSet,
    CycleViewSet,
    GroupViewSet,
    UserViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"candidates", CandidateViewSet)
router.register(r"cycles", CycleViewSet)
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns = [
    path('o/', include(oauth2_urls)),
    # iOS clients send username/password here to receive access + refresh tokens
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # iOS clients send refresh token here to receive a new access token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    path("", include(router.urls)),
]
