from rest_framework import permissions, viewsets

from ktbtracker.api.serializers import CandidateSerializer
from ktbtracker.models import Candidate


class CandidateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Candidate.objects.all().order_by("-cycle_id")
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]
