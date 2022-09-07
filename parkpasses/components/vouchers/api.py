import logging

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet

from parkpasses.components.cart.models import Cart, CartItem
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

        content_type = ContentType.objects.get_for_model(voucher)
        cart_item = CartItem(cart=cart, object_id=voucher.id, content_type=content_type)
        cart_item.save()
        if is_customer(self.request):
            CartUtils.increment_cart_item_count(self.request)
        if not cart.datetime_first_added_to:
            cart.datetime_first_added_to = timezone.now()
        cart.datetime_last_added_to = timezone.now()
        cart.save()
        logger.debug(str(self.request.session))

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


class InternalVoucherViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on vouchers.
    """

    search_fields = ["recipient_name", "recipient_email"]
    queryset = Voucher.objects.all()
    model = Voucher
    permission_classes = [IsInternal]
    serializer_class = InternalVoucherSerializer
    filter_backends = [SearchFilter, DatatablesFilterBackend]
    filterset_class = VoucherFilter


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
                logger.debug(
                    "voucher.remaining_balance = " + str(voucher.remaining_balance)
                )
                return Response(
                    {
                        "is_voucher_code_valid": True,
                        "balance_remaining": voucher.remaining_balance,
                    }
                )
        return Response({"is_voucher_code_valid": False})
