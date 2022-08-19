import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from parkpasses.components.orders.models import Order, OrderItem
from parkpasses.components.orders.serializers import (
    OrderItemSerializer,
    OrderSerializer,
)

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on orders.
    """

    model = Order
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.all()


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on order items.
    """

    model = OrderItem
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.all()
