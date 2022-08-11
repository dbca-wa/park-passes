from django.utils import timezone
from rest_framework import serializers

from parkpasses.components.discount_codes.models import (
    DiscountCode,
    DiscountCodeBatch,
    DiscountCodeBatchComment,
)


class InternalDiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = "__all__"


class ExternalDiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = [
            "code",
        ]


class InternalDiscountCodeBatchSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField()
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
