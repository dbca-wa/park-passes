from rest_framework import serializers

from parkpasses.components.concessions.models import Concession


class ExternalConcessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concession
        fields = ["id", "concession_type", "discount_percentage"]


class InternalConcessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concession
        fields = "__all__"
