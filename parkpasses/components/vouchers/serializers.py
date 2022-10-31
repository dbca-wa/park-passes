import logging

from django.conf import settings
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from parkpasses.components.users.serializers import BasicEmailUserSerializer
from parkpasses.components.vouchers.models import Voucher, VoucherTransaction
from parkpasses.helpers import is_parkpasses_payments_officer
from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class ExternalVoucherSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.CharField()

    class Meta:
        model = Voucher
        exclude = ["purchaser"]
        read_only_fields = [
            "id",
            "amount",
            "voucher_number",
            "expiry",
            "code",
            "datetime_purchased",
            "datetime_updated",
            "processing_status",
            "remaining_balance",
        ]


class ExternalListVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = [
            "id",
            "amount",
            "voucher_number",
            "recipient_name",
            "recipient_email",
            "personal_message",
            "expiry",
            "code",
            "datetime_to_email",
            "datetime_purchased",
            "datetime_updated",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        email_user = EmailUser.objects.get(id=instance.purchaser)
        logger.debug("email_user = " + str(email_user))
        data.update({"purchaser": BasicEmailUserSerializer(email_user).data})
        return data


class ExternalCreateVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = (
            "amount",
            "recipient_name",
            "recipient_email",
            "personal_message",
            "datetime_to_email",
        )


class ExternalUpdateVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        exclude = ["purchaser"]
        read_only_fields = [
            "id",
            "voucher_number",
            "voucher_number",
            "amount",
            "expiry",
            "code",
            "pin",
            "datetime_purchased",
            "datetime_updated",
            "processing_status",
        ]


class InternalVoucherSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.DecimalField(max_digits=8, decimal_places=2)
    processing_status = serializers.SerializerMethodField()
    pin = serializers.SerializerMethodField()
    purchaser_name = serializers.SerializerMethodField()
    user_can_view_payment_details = serializers.SerializerMethodField()

    class Meta:
        model = Voucher
        fields = "__all__"
        datatables_always_serialize = [
            "user_can_view_payment_details",
        ]

    def get_processing_status(self, obj):
        return obj.get_processing_status_display()

    def get_pin(self, obj):
        if is_parkpasses_payments_officer(self.context["request"]):
            return str(obj.pin)
        return f"Visible to [{settings.PAYMENTS_OFFICER_GROUP}] only"

    def get_purchaser_name(self, obj):
        return retrieve_email_user(obj.purchaser).get_full_name()

    def get_user_can_view_payment_details(self, obj):
        return is_parkpasses_payments_officer(self.context["request"])


class ExternalVoucherTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherTransaction
        fields = "__all__"


class InternalVoucherTransactionSerializer(serializers.ModelSerializer):
    original_amount = serializers.DecimalField(
        source="voucher.amount", max_digits=8, decimal_places=2
    )
    voucher_code = serializers.CharField(source="voucher.code")
    remaining_balance = serializers.DecimalField(
        source="voucher.remaining_balance", max_digits=8, decimal_places=2
    )

    class Meta:
        model = VoucherTransaction
        fields = [
            "credit",
            "debit",
            "voucher_code",
            "original_amount",
            "remaining_balance",
        ]
