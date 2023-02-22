import logging
import os

from rest_framework import serializers

from parkpasses.components.concessions.serializers import ExternalConcessionSerializer
from parkpasses.components.discount_codes.serializers import (
    ExternalDiscountCodeSerializer,
)
from parkpasses.components.parks.models import ParkGroup
from parkpasses.components.passes.models import (
    DistrictPassTypeDurationOracleCode,
    Pass,
    PassCancellation,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.components.vouchers.serializers import (
    ExternalVoucherSerializer,
    ExternalVoucherTransactionSerializer,
)
from parkpasses.helpers import (
    get_retailer_group_ids_for_user,
    is_parkpasses_officer,
    is_parkpasses_payments_officer,
    is_retailer,
)

logger = logging.getLogger(__name__)


class PassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "image",
            "display_name",
            "display_order",
        ]
        read_only_fields = [
            "id",
            "slug",
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


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = ["id", "name", "duration", "price"]


class InternalOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PassTypePricingWindowOption
        fields = "__all__"


class InternalCreatePricingWindowSerializer(serializers.ModelSerializer):
    pricing_options = serializers.ListField(write_only=True)

    class Meta:
        model = PassTypePricingWindow
        fields = [
            "name",
            "pass_type",
            "date_start",
            "date_expiry",
            "pricing_options",
        ]

    def validate(self, data):
        pass_type = data["pass_type"]
        default_options = (
            PassTypePricingWindowOption.get_default_options_by_pass_type_id(
                pass_type.id
            )
        )
        if len(data["pricing_options"]) != len(default_options):
            raise serializers.ValidationError(
                "A price must be provided for each of the default options."
            )
        return data

    def create(self, validated_data):
        options = validated_data.pop("pricing_options")
        pricing_window = PassTypePricingWindow.objects.create(**validated_data)
        default_options = (
            PassTypePricingWindowOption.get_default_options_by_pass_type_id(
                pricing_window.pass_type.id
            )
        )
        for index, default_option in enumerate(default_options):
            PassTypePricingWindowOption.objects.create(
                name=default_option.name,
                duration=default_option.duration,
                price=options[index],
                pricing_window=pricing_window,
            )
        return pricing_window


class InternalPricingWindowSerializer(serializers.ModelSerializer):
    options = InternalOptionSerializer(many=True)
    pass_type_display_name = serializers.ReadOnlyField(source="pass_type.display_name")
    status = serializers.CharField()

    class Meta:
        model = PassTypePricingWindow
        fields = [
            "id",
            "name",
            "pass_type_display_name",
            "pass_type",
            "date_start",
            "date_expiry",
            "options",
            "status",
        ]
        read_only_fields = [
            "pass_type_display_name",
            "status",
        ]
        datatables_always_serialize = [
            "id",
            "options",
        ]

    def update(self, instance, validated_data):
        options = validated_data.pop("options")
        validated_data.pop("status")  # read-only field
        instance = super().update(instance, validated_data)

        # update each option
        for option_data in options:
            option_id = option_data.get("id", None)
            if (
                option_id
                and PassTypePricingWindowOption.objects.filter(pk=option_id).exists()
            ):
                option = PassTypePricingWindowOption.objects.get(pk=option_id)
                option.name = option_data.get("name", option.name)
                option.duration = option_data.get("duration", option.duration)
                option.price = option_data.get("price", option.price)
                option.save()

        return instance


class PassTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTemplate
        fields = "__all__"


class PassModelCreateSerializer(serializers.ModelSerializer):
    """A base model serializer for passes that allows additonal fields to be submitted for processing"""

    rac_discount_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    discount_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    voucher_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    voucher_pin = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    concession_id = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    concession_card_number = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    concession_card_expiry_month = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    concession_card_expiry_year = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    sold_via = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        fields = [
            "rac_discount_code",
            "discount_code",
            "voucher_code",
            "voucher_pin",
            "concession_id",
            "concession_card_number",
            "concession_card_expiry_month",
            "concession_card_expiry_year",
            "sold_via",
        ]


class ExternalCreateHolidayPassSerializer(
    PassModelCreateSerializer
):  # user = serializers.IntegerField(write_only=True, required=False, allow_blank=True)
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateAnnualLocalPassSerializer(PassModelCreateSerializer):
    park_group = serializers.PrimaryKeyRelatedField(
        queryset=ParkGroup.objects.all(), many=False
    )

    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park_group",
            "postcode",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateAllParksPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateGoldStarPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "company",
            "address_line_1",
            "address_line_2",
            "suburb",
            "state",
            "postcode",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateDayEntryPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreatePinjarOffRoadPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "drivers_licence_number",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalPassSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    price = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    pass_type = serializers.SerializerMethodField()
    pass_type_name = serializers.SerializerMethodField()
    pass_type_image = serializers.CharField(
        source="option.pricing_window.pass_type.image.url"
    )
    park_group = serializers.CharField()
    concession = serializers.SerializerMethodField()
    rac_discount_percentage = serializers.SerializerMethodField()
    price_after_concession_applied = serializers.CharField()
    discount_code = serializers.SerializerMethodField()
    price_after_discount_code_applied = serializers.CharField()
    voucher = serializers.SerializerMethodField()
    voucher_transaction = ExternalVoucherTransactionSerializer()
    price_after_voucher_applied = serializers.CharField()
    sold_via_name = serializers.SerializerMethodField(read_only=True)
    sold_internally = serializers.BooleanField(read_only=True)
    date_start_formatted = serializers.DateField(
        source="date_start", read_only=True, format="%d/%m/%Y"
    )
    date_expiry_formatted = serializers.DateField(
        source="date_expiry", read_only=True, format="%d/%m/%Y"
    )

    class Meta:
        model = Pass
        fields = [
            "id",
            "pass_number",
            "option",
            "pass_type",
            "pass_type_name",
            "pass_type_image",
            "price",
            "duration",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "company",
            "address_line_1",
            "address_line_2",
            "suburb",
            "state",
            "postcode",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "prevent_further_vehicle_updates",
            "drivers_licence_number",
            "park_group",
            "park_pass_pdf",
            "date_start",
            "date_start_formatted",
            "date_expiry_formatted",
            "date_expiry",
            "renew_automatically",
            "status",
            "status_display",
            "datetime_created",
            "datetime_updated",
            "rac_discount_percentage",
            "concession",
            "price_after_concession_applied",
            "discount_code",
            "price_after_discount_code_applied",
            "voucher",
            "voucher_transaction",
            "price_after_voucher_applied",
            "sold_via_name",
            "sold_internally",
        ]
        read_only_fields = [
            "id",
            "pass_number",
            "pass_type",
            "pass_type_name",
            "price",
            "park_group",
            "date_start_formatted",
            "date_expiry_formatted",
            "date_expiry",
            "park_pass_pdf",
            "status",
            "status_display",
            "datetime_created",
            "datetime_updated",
            "concession",
            "price_after_concession_applied",
            "discount_code",
            "price_after_discount_code_applied",
            "voucher",
            "voucher_transaction",
            "price_after_voucher_applied",
            "sold_via_name",
        ]

    def get_sold_via_name(self, obj):
        return obj.sold_via.organisation["organisation_name"]

    def get_price(self, obj):
        return f"{obj.option.price:.2f}"

    def get_pass_type(self, obj):
        return obj.option.pricing_window.pass_type.display_name

    def get_pass_type_name(self, obj):
        return obj.option.pricing_window.pass_type.name

    def get_duration(self, obj):
        return f"{obj.option.duration} days"

    def get_rac_discount_percentage(self, obj):
        if hasattr(obj, "rac_discount_usage"):
            return obj.rac_discount_usage.discount_percentage
        return None

    def get_concession(self, obj):
        if hasattr(obj, "concession_usage"):
            concession = obj.concession_usage.concession
            serializer = ExternalConcessionSerializer(concession)
            return serializer.data
        return None

    def get_discount_code(self, obj):
        if hasattr(obj, "discount_code_usage"):
            discount_code = obj.discount_code_usage.discount_code
            serializer = ExternalDiscountCodeSerializer(discount_code)
            return serializer.data
        return None

    def get_voucher(self, obj):
        if hasattr(obj, "voucher_transaction"):
            voucher = obj.voucher_transaction.voucher
            serializer = ExternalVoucherSerializer(voucher)
            return serializer.data
        return None


class ExternalQRCodePassSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField()
    park_group = serializers.SerializerMethodField()
    vehicle_registration_1 = serializers.SerializerMethodField()
    vehicle_registration_2 = serializers.SerializerMethodField()

    class Meta:
        model = Pass
        fields = [
            "pass_type",
            "park_group",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "date_start",
            "date_expiry",
            "vehicle_registration_1",
            "vehicle_registration_2",
        ]

    def get_park_group(self, obj):
        if obj.park_group:
            return str(obj.park_group)
        return ""

    def get_vehicle_registration_1(self, obj):
        if obj.vehicle_registration_1:
            return obj.vehicle_registration_1
        return ""

    def get_vehicle_registration_2(self, obj):
        if obj.vehicle_registration_2:
            return obj.vehicle_registration_2
        return ""


class ExternalUpdatePassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = [
            "renew_automatically",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "prevent_further_vehicle_updates",
        ]

    def validate(self, data):
        if data["prevent_further_vehicle_updates"]:
            if data["vehicle_registration_1"]:
                raise serializers.ValidationError(
                    "Updating vehicle registration has been prevented for this pass."
                )
            if data["vehicle_registration_2"]:
                raise serializers.ValidationError(
                    "Updating vehicle registration has been prevented for this pass."
                )
        return data


class RetailerUpdatePassSerializer(serializers.ModelSerializer):
    duration = serializers.CharField(source="option.name", read_only=True)
    date_expiry = serializers.CharField(read_only=True)

    class Meta:
        model = Pass
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "duration",
            "date_start",
            "date_expiry",
            "vehicle_registration_1",
            "vehicle_registration_2",
        ]
        read_only_fields = ["id"]


class InternalPassRetrieveSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(
        source="option.pricing_window.pass_type", read_only=True
    )
    pass_type_name = serializers.CharField(
        source="option.pricing_window.pass_type.name", read_only=True
    )
    pricing_window = serializers.CharField(source="option.pricing_window")
    duration = serializers.CharField(source="option.name")
    park_pass_pdf = serializers.SerializerMethodField()
    sold_via = serializers.PrimaryKeyRelatedField(queryset=RetailerGroup.objects.all())
    sold_via_name = serializers.SerializerMethodField(read_only=True)
    processing_status_display_name = serializers.CharField(
        source="status_display", read_only=True
    )
    concession_type = serializers.CharField(
        source="concession_usage.concession.concession_type",
        read_only=True,
        required=False,
    )
    concession_discount_percentage = serializers.CharField(
        source="concession_usage.concession.discount_percentage",
        read_only=True,
        required=False,
    )
    concession_card_number = serializers.CharField(
        source="concession_usage.concession_card_number",
        read_only=True,
        required=False,
    )
    rac_discount_used = serializers.CharField(
        source="rac_discount_usage", required=False
    )
    rac_discount_percentage = serializers.CharField(
        source="rac_discount_usage.discount_percentage", required=False
    )
    discount_code_used = serializers.CharField(
        source="discount_code_usage.discount_code.code", required=False
    )
    discount_code_discount = serializers.SerializerMethodField(
        read_only=True, required=False
    )
    voucher_number = serializers.CharField(
        source="voucher_transaction.voucher.voucher_number",
        read_only=True,
        required=False,
    )
    voucher_code = serializers.CharField(
        source="voucher_transaction.voucher.code",
        read_only=True,
        required=False,
    )
    voucher_transaction_amount = serializers.CharField(
        source="voucher_transaction.debit"
    )
    user_can_edit = serializers.SerializerMethodField()
    invoice_link = serializers.CharField(read_only=True)

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = [
            "pass_type",
            "pricing_window",
            "sold_via",
            "sold_via_name",
            "pass_type_name",
            "concession_type",
            "concession_discount_percentage",
            "rac_discount_percentage",
            "invoice_link",
        ]
        datatables_always_serialize = [
            "user_can_edit",
        ]

    def get_sold_via_name(self, obj):
        return obj.sold_via.organisation["organisation_name"]

    def get_discount_code_discount(self, obj):
        if hasattr(obj, "discount_code_usage"):
            discount = (
                obj.discount_code_usage.discount_code.discount_code_batch.discount_amount
            )
            if discount:
                return f"${discount}"
            discount = (
                obj.discount_code_usage.discount_code.discount_code_batch.discount_percentage
            )
            return f"{discount}% Off"
        return None

    def get_park_pass_pdf(self, obj):
        return os.path.basename(obj.park_pass_pdf.name)

    def get_user_can_edit(self, obj):
        request = self.context["request"]
        if is_retailer(request):
            retailer_group_ids = get_retailer_group_ids_for_user(request)
            if obj.sold_via_id in retailer_group_ids:
                return True
        return is_parkpasses_payments_officer(
            self.context["request"]
        ) or is_parkpasses_officer(self.context["request"])


class InternalPassSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(
        source="option.pricing_window.pass_type", read_only=True
    )
    pricing_window = serializers.CharField(source="option.pricing_window")
    park_pass_pdf = serializers.SerializerMethodField()
    sold_via = serializers.PrimaryKeyRelatedField(queryset=RetailerGroup.objects.all())
    sold_via_name = serializers.SerializerMethodField(read_only=True)
    processing_status_display_name = serializers.CharField(
        source="status_display", read_only=True
    )
    pro_rata_refund_amount_display = serializers.CharField(read_only=True)
    user_can_view_payment_details = serializers.SerializerMethodField()
    user_can_upload_personnel_passes = serializers.SerializerMethodField()
    user_can_edit_and_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = ["pass_type", "pricing_window", "sold_via", "sold_via_name"]
        datatables_always_serialize = [
            "date_expiry",
            "processing_status",
            "pro_rata_refund_amount_display",
            "user_can_view_payment_details",
            "user_can_upload_personnel_passes",
            "user_can_edit_and_cancel",
        ]

    def get_sold_via_name(self, obj):
        return obj.sold_via.organisation["organisation_name"]

    def get_park_pass_pdf(self, obj):
        return os.path.basename(obj.park_pass_pdf.name)

    def get_user_can_view_payment_details(self, obj):
        return is_parkpasses_payments_officer(self.context["request"])

    def get_user_can_upload_personnel_passes(self, obj):
        return is_parkpasses_officer(self.context["request"])

    def get_user_can_edit_and_cancel(self, obj):
        request = self.context["request"]
        if request.user.is_superuser:
            return True
        return is_parkpasses_payments_officer(
            self.context["request"]
        ) or is_parkpasses_officer(self.context["request"])


class RetailerApiCreatePassSerializer(serializers.ModelSerializer):
    rac_member_number = serializers.CharField(required=True)
    postcode = serializers.CharField(required=True)
    in_cart = serializers.HiddenField(default=False)
    sold_via = serializers.ReadOnlyField()

    class Meta:
        model = Pass
        fields = [
            "id",
            "rac_member_number",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "postcode",
            "company",
            "address_line_1",
            "address_line_2",
            "suburb",
            "state",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park_group",
            "date_start",
            "in_cart",
            "sold_via",
        ]
        extra_kwargs = {"mobile": {"required": True, "allow_blank": False}}


class InternalPassCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassCancellation
        fields = "__all__"


class InternalPassTypesOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = "__all__"


class InternalDistrictPassTypeDurationOracleCodeSerializer(serializers.ModelSerializer):
    district_name = serializers.SerializerMethodField()
    option_name = serializers.CharField(source="option.name", read_only=True)
    pass_type_name = serializers.CharField(
        source="option.pricing_window.pass_type.name", read_only=True
    )
    pass_type_display_name = serializers.CharField(
        source="option.pricing_window.pass_type.display_name", read_only=True
    )

    class Meta:
        model = DistrictPassTypeDurationOracleCode
        fields = [
            "id",
            "district",
            "district_name",
            "pass_type_name",
            "pass_type_display_name",
            "option",
            "option_name",
            "oracle_code",
        ]

    def get_district_name(self, obj):
        if obj.district:
            return obj.district.name
        return "PICA (Online Sales)"


class InternalDistrictPassTypeDurationOracleCodeListUpdateSerializer(
    serializers.ModelSerializer
):
    id = serializers.IntegerField()

    class Meta:
        model = DistrictPassTypeDurationOracleCode
        fields = [
            "id",
            "oracle_code",
        ]
