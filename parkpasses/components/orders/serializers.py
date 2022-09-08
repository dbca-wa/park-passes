from rest_framework import serializers

from parkpasses.components.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderListItemSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()
    items = OrderItemSerializer(many=True, read_only=True)
    invoice_link = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "uuid",
            "invoice_reference",
            "invoice_link",
            "datetime_created",
            "total",
            "items",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "uuid",
            "invoice_reference",
            "invoice_link",
            "datetime_created",
            "total",
            "items",
        ]
