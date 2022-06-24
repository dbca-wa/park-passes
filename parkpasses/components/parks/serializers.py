from rest_framework import serializers

from parkpasses.components.parks.models import LGA, Park, Postcode


class PostcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postcode
        fields = "__all__"


class ParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Park
        fields = "__all__"


class LGASerializer(serializers.ModelSerializer):
    class Meta:
        model = LGA
        fields = "__all__"
