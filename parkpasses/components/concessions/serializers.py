from rest_framework import serializers

from parkpasses.components.concessions.models import Concession


class ConcessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concession
        fields = ["id", "concession_type"]


class InternalConcessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concession
        fields = "__all__"
