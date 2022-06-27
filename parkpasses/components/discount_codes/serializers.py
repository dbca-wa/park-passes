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


class InternalDiscountCodeBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCodeBatch
        fields = "__all__"
        datatables_always_serialize = ("id",)


class InternalDiscountCodeBatchCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCodeBatchComment
        fields = "__all__"
