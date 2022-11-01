import logging

import requests
from django.http import FileResponse, Http404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.orders.models import Order, OrderItem
from parkpasses.components.orders.serializers import (
    OrderItemSerializer,
    OrderSerializer,
)
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class ExternalOrderByUUID(RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id)


class SmallResultSetPagination(DatatablesPageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 1000


class ExternalOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    model = Order
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = SmallResultSetPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id).order_by(
            "-datetime_created"
        )

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice")
    def retrieve_invoice(self, request, *args, **kwargs):
        order = self.get_object()
        invoice_url = order.invoice_link
        if invoice_url:
            response = requests.get(invoice_url)
            return FileResponse(response, content_type="application/pdf")

        raise Http404


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
