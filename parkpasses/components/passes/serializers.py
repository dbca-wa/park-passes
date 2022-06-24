from rest_framework import serializers

from parkpasses.components.passes.models import (
    Pass,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)


class PassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = [
            "id",
            "image",
            "display_name",
            "display_order",
        ]
        read_only_fields = [
            "id",
            "image",
            "display_name",
            "display_order",
        ]


class InternalPassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = "__all__"


class PassTypePricingWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = [
            "id",
            "image",
            "display_name",
            "display_order",
        ]
        read_only_fields = [
            "id",
            "image",
            "display_name",
            "display_order",
        ]


class PricingWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindow
        fields = "__all__"


class PassTypePricingWindowOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = "__all__"


class PassTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = "__all__"


class PassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = "__all__"
