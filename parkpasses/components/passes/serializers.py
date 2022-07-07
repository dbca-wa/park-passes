from django.conf import settings
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
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
            "image",
            "display_name",
            "display_order",
        ]
        read_only_fields = [
            "id",
            "name",
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
    user = serializers.SerializerMethodField()
    sold_via = serializers.SerializerMethodField()

    def get_user(self, obj):
        try:
            email_user = EmailUser.objects.get(email=obj.email)
        except EmailUser.DoesNotExist:
            email_user = EmailUser(
                email=obj.email, first_name=obj.first_name, last_name=obj.last_name
            )
            email_user.save()
            email_user = EmailUser.objects.get(email=obj.email)

        return email_user.id

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
            "park",
            "datetime_start",
            "datetime_expiry",
            "renew_automatically",
            "processing_status",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ]


class ExternalPassSerializer(serializers.ModelSerializer):
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
            "pass_number",
            "park",
            "datetime_start",
            "datetime_expiry",
            "park_pass_pdf",
            "processing_status",
            "datetime_created",
            "datetime_updated",
            "sold_via",
        ]


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
