
from rest_framework import serializers

from ktbtracker.models import Candidate


class CandidateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Candidate
        fields = "__all__"
