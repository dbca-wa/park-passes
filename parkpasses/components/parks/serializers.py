from rest_framework import serializers

from parkpasses.components.parks.models import LGA, Park, ParkGroup, Postcode


class PostcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postcode
        fields = "__all__"


class ParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Park
        fields = "__all__"


class ExternalParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Park
        fields = ["id", "name"]


class LGASerializer(serializers.ModelSerializer):
    class Meta:
        model = LGA
        fields = "__all__"


class ExternalParkGroupSerializer(serializers.ModelSerializer):
    parks = ExternalParkSerializer(many=True)

    class Meta:
        model = ParkGroup
        fields = [
            "id",
            "name",
            "parks",
        ]
