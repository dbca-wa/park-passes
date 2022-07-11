import logging

from rest_framework import serializers

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction

logger = logging.getLogger(__name__)


class ExternalVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        exclude = ["purchaser"]
        read_only_fields = [
            "id",
            "voucher_number",
            "expiry",
            "code",
            "datetime_purchased",
            "datetime_updated",
            "processing_status",
        ]


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
    class Meta:
        model = Voucher
        fields = "__all__"


class VoucherTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherTransaction
        fields = ["id", "voucher_number"]


class InternalVoucherTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherTransaction
        fields = "__all__"
