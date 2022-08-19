from rest_framework import serializers

from parkpasses.components.retailers.models import RetailerGroup


class RetailerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerGroup
        fields = "__all__"
