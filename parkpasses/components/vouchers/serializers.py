import logging

from ledger_api_client.ledger_models import EmailUserRO as EmailUser
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
    purchaser_email = serializers.EmailField(allow_blank=False)
    purchaser_first_name = serializers.CharField(write_only=True)
    purchaser_last_name = serializers.CharField(write_only=True)

    class Meta:
        model = Voucher
        fields = (
            "purchaser",
            "amount",
            "recipient_name",
            "recipient_email",
            "personal_message",
            "datetime_to_email",
            "purchaser_email",
            "purchaser_first_name",
            "purchaser_last_name",
        )
        read_only_fields = ("purchaser",)

    def create(self, validated_data):
        logger.debug("validated_data = " + str(validated_data))
        try:
            email_user = EmailUser.objects.get(email=validated_data["purchaser_email"])
        except EmailUser.DoesNotExist:
            email_user = EmailUser(
                email=validated_data["purchaser_email"],
                first_name=validated_data["purchaser_first_name"],
                last_name=validated_data["purchaser_last_name"],
            )
            email_user.save()
            email_user = EmailUser.objects.get(email=validated_data["purchaser_email"])
        logger.debug("email_user = " + str(email_user))
        validated_data["purchaser"] = email_user.id
        return super().create(validated_data)


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
