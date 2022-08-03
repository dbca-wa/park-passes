from django.conf import settings
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
            "name",
            "description",
            "image",
            "display_name",
            "display_order",
        ]
        read_only_fields = [
            "id",
            "name",
            "description",
            "image",
            "display_name",
            "display_order",
        ]


class InternalPassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = "__all__"


class InternalPricingWindowSerializer(serializers.ModelSerializer):
    pass_type = serializers.PrimaryKeyRelatedField(queryset=PassType.objects.all())
    pass_type_display_name = serializers.ReadOnlyField(source="pass_type.display_name")

    class Meta:
        model = PassTypePricingWindow
        fields = [
            "id",
            "name",
            "pass_type_display_name",
            "pass_type",
            "date_start",
            "date_expiry",
        ]
        read_only_fields = [
            "pass_type_display_name",
        ]

    # def get_pass_type_display_name(self, obj):
    #    return obj.pass_type.display_name


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = ["id", "name", "duration", "price"]


class InternalOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = "__all__"


class PassTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTemplate
        fields = "__all__"


class ExternalCreatePassSerializer(serializers.ModelSerializer):
    sold_via = serializers.SerializerMethodField()

    def get_sold_via(self, obj):
        return getattr(obj, "sold_via", settings.PARKPASSES_DEFAULT_SOLD_VIA)

    class Meta:
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park_group",
            "renew_automatically",
            "sold_via",
            "datetime_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ]


class ExternalPassSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    pass_type = serializers.SerializerMethodField()

    class Meta:
        model = Pass
        fields = [
            "id",
            "pass_number",
            "option",
            "pass_type",
            "price",
            "duration",
            "first_name",
            "last_name",
            "email",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park_group",
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
            "pass_number",
            "pass_type",
            "price",
            "park_group",
            "datetime_expiry",
            "park_pass_pdf",
            "processing_status",
            "datetime_created",
            "datetime_updated",
            "sold_via",
        ]

    def get_price(self, obj):
        return f"{obj.option.price:.2f}"

    def get_pass_type(self, obj):
        return obj.option.pricing_window.pass_type.display_name

    def get_duration(self, obj):
        return f"{obj.option.duration} days"


class ExternalUpdatePassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = [
            "vehicle_registration_1",
            "vehicle_registration_2",
        ]


class InternalPassSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(source="option.pricing_window.pass_type")
    pricing_window = serializers.CharField(source="option.pricing_window")
    sold_via = serializers.CharField(source="sold_via.name")

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = ["pass_type", "pricing_window", "sold_via"]
        datatables_always_serialize = [
            "id",
            "pass_number",
            "option",
            "first_name",
            "last_name",
            "email",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park_group",
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
