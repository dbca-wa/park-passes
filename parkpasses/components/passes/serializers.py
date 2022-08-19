from rest_framework import serializers

from parkpasses.components.passes.models import (
    Pass,
    PassCancellation,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.retailers.models import RetailerGroup


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


class InternalPassRetrieveSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(
        source="option.pricing_window.pass_type", read_only=True
    )
    pricing_window = serializers.CharField(source="option.pricing_window")
    sold_via = serializers.PrimaryKeyRelatedField(queryset=RetailerGroup.objects.all())
    sold_via_name = serializers.CharField(source="sold_via.name", read_only=True)
    processing_status_display_name = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )
    discount_code_used = serializers.CharField(
        source="discountcodeusage.discount_code.code", required=False
    )
    discount_code_discount = serializers.SerializerMethodField(
        read_only=True, required=False
    )
    voucher_number = serializers.CharField(
        source="vouchertransaction.voucher.voucher_number",
        read_only=True,
        required=False,
    )
    voucher_transaction_amount = serializers.CharField(
        source="vouchertransaction.voucher.amount"
    )
    concession_type = serializers.CharField(
        source="concessionusage.concession.concession_type",
        read_only=True,
        required=False,
    )
    concession_discount_percentage = serializers.CharField(
        source="concessionusage.concession.discount_percentage",
        read_only=True,
        required=False,
    )

    def get_discount_code_discount(self, obj):
        if hasattr(obj, "discountcodeusage"):
            discount = (
                obj.discountcodeusage.discount_code.discount_code_batch.discount_amount
            )
            if discount:
                return f"${discount}"
            discount = (
                obj.discountcodeusage.discount_code.discount_code_batch.discount_percentage
            )
            return f"{discount}% Off"
        return None

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = ["pass_type", "pricing_window", "sold_via", "sold_via_name"]


class InternalPassSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(
        source="option.pricing_window.pass_type", read_only=True
    )
    pricing_window = serializers.CharField(source="option.pricing_window")
    sold_via = serializers.PrimaryKeyRelatedField(queryset=RetailerGroup.objects.all())
    sold_via_name = serializers.CharField(source="sold_via.name", read_only=True)
    processing_status_display_name = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = ["pass_type", "pricing_window", "sold_via", "sold_via_name"]
        datatables_always_serialize = [
            "id",
            "pass_number",
            "sold_via",
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
            "processing_status_display_name",
            "datetime_created",
            "datetime_updated",
        ]


class InternalPassCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassCancellation
        fields = "__all__"
