from rest_framework import serializers

from parkpasses.components.discount_codes.models import DiscountCode


class InternalDiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = "__all__"
