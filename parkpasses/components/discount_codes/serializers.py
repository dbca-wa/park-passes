from django.utils import timezone
from rest_framework import serializers

from parkpasses.components.discount_codes.models import (
    DiscountCode,
    DiscountCodeBatch,
    DiscountCodeBatchComment,
    DiscountCodeBatchValidPassType,
    DiscountCodeBatchValidUser,
)


class InternalDiscountCodeXlsxSerializer(serializers.ModelSerializer):
    discount_code_batch = serializers.ReadOnlyField(
        source="discount_code_batch.discount_code_batch_number"
    )
    remaining_uses = serializers.ReadOnlyField()

    class Meta:
        model = DiscountCode
        fields = ["discount_code_batch", "code", "remaining_uses"]


class InternalDiscountCodeSerializer(serializers.ModelSerializer):
    remaining_uses = serializers.ReadOnlyField()

    class Meta:
        model = DiscountCode
        fields = ["id", "code", "discount_code_batch", "remaining_uses"]


class ExternalDiscountCodeSerializer(serializers.ModelSerializer):
    discount_type = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    class Meta:
        model = DiscountCode
        fields = [
            "code",
            "discount_type",
            "discount",
        ]

    def get_discount_type(self, obj):
        if obj.discount_code_batch.discount_percentage:
            return "percentage"
        return "amount"

    def get_discount(self, obj):
        if obj.discount_code_batch.discount_percentage:
            return obj.discount_code_batch.discount_percentage
        return obj.discount_code_batch.discount_amount


class ValidPassTypeSerializer(serializers.ModelSerializer):
    pass_type_display_name = serializers.StringRelatedField(
        source="pass_type.display_name"
    )

    class Meta:
        model = DiscountCodeBatchValidPassType
        fields = [
            "pass_type_id",
            "pass_type_display_name",
        ]


class ValidUserSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = DiscountCodeBatchValidUser
        fields = [
            "user",
            "display_name",
        ]


class InternalDiscountCodeBatchSerializer(serializers.ModelSerializer):
    discount_codes = InternalDiscountCodeSerializer(many=True, read_only=True)
    valid_pass_types = ValidPassTypeSerializer(many=True, read_only=True)
    valid_users = ValidUserSerializer(many=True, read_only=True)
    created_by_name = serializers.ReadOnlyField()
    datetime_start = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    datetime_expiry = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    status = serializers.SerializerMethodField()

    class Meta:
        model = DiscountCodeBatch
        fields = [
            "id",
            "created_by_name",
            "discount_code_batch_number",
            "datetime_start",
            "datetime_expiry",
            "codes_to_generate",
            "times_each_code_can_be_used",
            "invalidated",
            "discount_amount",
            "discount_percentage",
            "datetime_created",
            "datetime_updated",
            "status",
            "valid_pass_types",
            "valid_users",
            "discount_codes",
        ]
        read_only_fields = [
            "created_by_name",
        ]
        datatables_always_serialize = ("id",)

    def get_status(self, obj):
        if obj.datetime_start >= timezone.now():
            return "Future"
        elif obj.datetime_expiry < timezone.now():
            return "Expired"
        else:
            return "Current"


class InternalDiscountCodeBatchCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCodeBatchComment
        fields = "__all__"
