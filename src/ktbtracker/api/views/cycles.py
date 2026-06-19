import logging

from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils import debug

from ktbtracker.models import Cycle
from api.serializers import CycleSerializer

logger = logging.getLogger(__name__)


class CycleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Cycle.objects.all().order_by("-id")
    serializer_class = CycleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated] # [permissions.AllowAny]

    @debug
    def list(self, request, *args, **kwargs):
        logger.debug(f"list {request.user=}")
        return super().list(request, *args, **kwargs)
