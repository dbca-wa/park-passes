import logging

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from parkpasses.components.orders.models import Order, OrderItem
from parkpasses.components.orders.serializers import (
    OrderItemSerializer,
    OrderSerializer,
)
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class ExternalOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    model = Order
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id)


class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on orders.
    """

    model = Order
    permission_classes = [IsInternal]
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
