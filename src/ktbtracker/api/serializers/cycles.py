from django.contrib.auth.models import Group
from rest_framework import serializers

from ktbtracker.models import Cycle


class CycleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cycle
        fields = "__all__"
