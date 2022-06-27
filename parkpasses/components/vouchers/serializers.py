from rest_framework import serializers

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ["id", "voucher_number"]


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
