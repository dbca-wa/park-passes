import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.filters import DatatablesFilterBackend

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.main.api import (
    CustomDatatablesListMixin,
    CustomDatatablesRenderer,
)
from parkpasses.components.orders.models import OrderItem
from parkpasses.components.vouchers.models import Voucher, VoucherTransaction
from parkpasses.components.vouchers.serializers import (
    ExternalCreateVoucherSerializer,
    ExternalUpdateVoucherSerializer,
    ExternalVoucherSerializer,
    ExternalVoucherTransactionSerializer,
    InternalVoucherSerializer,
    InternalVoucherTransactionSerializer,
)
from parkpasses.helpers import is_customer, is_internal
from parkpasses.permissions import IsInternal, IsInternalOrReadOnly

from ..cart.utils import CartUtils

logger = logging.getLogger(__name__)


class ExternalVoucherViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for external users to perform actions on their vouchers.
    """

    model = Voucher
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if "update" == self.action or "partial_update" == self.action:
            return ExternalUpdateVoucherSerializer
        elif "create" == self.action:
            return ExternalCreateVoucherSerializer
        return ExternalVoucherSerializer

    def get_queryset(self):
        return Voucher.objects.filter(purchaser=self.request.user.id)

    def perform_create(self, serializer):
        if is_customer(self.request):
            voucher = serializer.save(purchaser=self.request.user.id)
        else:
            voucher = serializer.save()

        cart = Cart.get_or_create_cart(self.request)
        logger.info(
            f"Retrieving cart for user: {self.request.user.id} ({self.request.user})"
        )

        content_type = ContentType.objects.get_for_model(voucher)
        cart_item = CartItem(cart=cart, object_id=voucher.id, content_type=content_type)
        cart_item.save()
        logger.info(f"Added cart item: {cart_item}")

        if is_customer(self.request):
            cart_item_count = CartUtils.increment_cart_item_count(self.request)
            logger.info(
                f"Incremented cart item count to {cart_item_count} -> {cart}",
            )

        if not cart.datetime_first_added_to:
            cart.datetime_first_added_to = timezone.now()
            logger.info(
                f"Assigned date first added to: {cart.datetime_first_added_to} to {cart}",
            )

        cart.datetime_last_added_to = timezone.now()
        logger.info(
            f"Assigned date last added to: {cart.datetime_first_added_to} to {cart}"
        )
        logger.info(f"Saving cart: {cart}")
        cart.save()
        logger.info("Cart saved.")

    def has_object_permission(self, request, view, obj):
        if "create" == view.action:
            return True
        if "update" == view.action:
            if is_customer(self.request):
                if obj.purchaser:
                    if obj.purchaser == request.user.id:
                        return True
        return False


class VoucherFilter(DatatablesFilterSet):
    datetime_to_email_from = filters.DateFilter(
        field_name="datetime_to_email", lookup_expr="gte"
    )
    datetime_to_email_to = filters.DateFilter(
        field_name="datetime_to_email", lookup_expr="lte"
    )

    class Meta:
        model = Voucher
        fields = "__all__"


class VoucherFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        processing_status = request.GET.get("processing_status")

        datetime_to_email_from = request.GET.get("datetime_to_email_from")
        datetime_to_email_to = request.GET.get("datetime_to_email_to")

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

        if datetime_to_email_from:
            queryset = queryset.filter(datetime_to_email__gte=datetime_to_email_from)

        if datetime_to_email_to:
            queryset = queryset.filter(datetime_to_email__lte=datetime_to_email_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class InternalVoucherViewSet(CustomDatatablesListMixin, viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on vouchers.
    """

    search_fields = ["recipient_name", "recipient_email"]
    queryset = Voucher.objects.exclude(in_cart=True)
    model = Voucher
    permission_classes = [IsInternal]
    serializer_class = InternalVoucherSerializer
    filter_backends = (VoucherFilterBackend,)
    filterset_class = VoucherFilter
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice")
    def retrieve_invoice(self, request, *args, **kwargs):
        voucher = self.get_object()
        content_type = ContentType.objects.get_for_model(Voucher)
        if OrderItem.objects.filter(
            object_id=voucher.id, content_type=content_type
        ).exists():
            order_item = OrderItem.objects.get(
                object_id=voucher.id, content_type=content_type
            )
            invoice_url = order_item.order.invoice_link
            if invoice_url:
                response = requests.get(invoice_url)
                return FileResponse(response, content_type="application/pdf")

        raise Http404

    @action(methods=["GET"], detail=True, url_path="payment-details")
    def payment_details(self, request, *args, **kwargs):
        voucher = self.get_object()
        content_type = ContentType.objects.get_for_model(Voucher)
        if OrderItem.objects.filter(
            object_id=voucher.id, content_type=content_type
        ).exists():
            order_item = OrderItem.objects.get(
                object_id=voucher.id, content_type=content_type
            )
            invoice_reference = order_item.order.invoice_reference
            return redirect(
                settings.LEDGER_UI_URL
                + "/ledger/payments/oracle/payments?invoice_no="
                + invoice_reference
            )

        raise Http404


class VoucherTransactionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on voucher transactions.
    """

    model = VoucherTransaction
    permission_classes = [IsInternalOrReadOnly]

    def get_queryset(self):
        return VoucherTransaction.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalVoucherTransactionSerializer
        else:
            return ExternalVoucherTransactionSerializer


class ValidateVoucherView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, format=None):
        email = request.query_params.get("email", None)
        code = request.query_params.get("code", None)
        pin = request.query_params.get("pin", None)

        if email and code and pin:
            logger.info(
                "Validating voucher with email: {}, code: {}, pin: {}".format(
                    email, code, pin
                ),
            )
            if Voucher.objects.filter(
                in_cart=False,
                recipient_email=email,
                code=code,
                pin=pin,
                processing_status=Voucher.DELIVERED,
            ).exists():
                voucher = Voucher.objects.get(
                    in_cart=False,
                    recipient_email=email,
                    code=code,
                    pin=pin,
                    processing_status=Voucher.DELIVERED,
                )
                logger.info(
                    f"Voucher exists: {voucher}.",
                )
                if voucher.remaining_balance > Decimal(0.00):
                    logger.info(
                        f"Voucher remaining balance: {voucher.remaining_balance}.",
                    )
                    return Response(
                        {
                            "is_voucher_code_valid": True,
                            "balance_remaining": voucher.remaining_balance,
                        }
                    )
                logger.info(
                    f"Voucher exists: {voucher} but has no remaining balance. Returning is_voucher_code_valid=false.",
                )
        return Response({"is_voucher_code_valid": False})
