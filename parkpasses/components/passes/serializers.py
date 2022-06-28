from rest_framework import serializers

from parkpasses.components.passes.models import (
    Pass,
    PassCancellation,
    PassTemplate,
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
        model = PassTemplate
        fields = "__all__"


class PassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = [
            "id",
            "pass_number",
            "option",
            "first_name",
            "last_name",
            "email",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park",
            "datetime_start",
            "datetime_expiry",
            "renew_automatically",
            "processing_status",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ]
        read_only_fields = [
            "id",
            "park",
            "datetime_start",
            "datetime_expiry",
            "park_pass_pdf",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ]

    # def __init__(self, *args, **kwargs):
    #    super(PassSerializer, self).__init__(*args, **kwargs)
    #    if settings.ANNUAL_LOCAL_PASS ==
    #    if "park" in self.fields.keys():
    #        self.fields.pop("park")


class InternalPassSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(source="option.pricing_window.pass_type")
    pricing_window = serializers.CharField(source="option.pricing_window")

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = ["pass_type", "pricing_window"]
        datatables_always_serialize = [
            "id",
            "pass_number",
            "option",
            "first_name",
            "last_name",
            "email",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park",
            "datetime_start",
            "datetime_expiry",
            "renew_automatically",
            "processing_status",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ]


class InternalPassCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassCancellation
        fields = "__all__"
