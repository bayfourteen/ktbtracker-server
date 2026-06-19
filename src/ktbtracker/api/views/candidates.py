from rest_framework import permissions, viewsets

from ktbtracker.models import Candidate
from api.serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Candidate.objects.all().order_by("-cycle_id")
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]
