import logging

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.vouchers.models import Voucher, VoucherTransaction
from parkpasses.components.vouchers.serializers import (
    ExternalCreateVoucherSerializer,
    ExternalUpdateVoucherSerializer,
    ExternalVoucherSerializer,
    InternalVoucherSerializer,
    InternalVoucherTransactionSerializer,
    VoucherTransactionSerializer,
)
from parkpasses.helpers import is_customer, is_internal
from parkpasses.permissions import IsInternal

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
        if self.request.session.get("cart_id", None):
            cart_id = self.request.session["cart_id"]
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart()
            cart.save()
            self.request.session["cart_id"] = cart.id
        content_type = ContentType.objects.get_for_model(voucher)
        cart_item = CartItem(cart=cart, object_id=voucher.id, content_type=content_type)
        cart_item.save()
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


class InternalVoucherViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on vouchers.
    """

    queryset = Voucher.objects.all()
    model = Voucher
    permission_classes = [IsInternal]
    serializer_class = InternalVoucherSerializer


class VoucherTransactionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on voucher transactions.
    """

    model = VoucherTransaction
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VoucherTransaction.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalVoucherTransactionSerializer
        else:
            return VoucherTransactionSerializer


class ValidateVoucherView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, format=None):
        recipient_email = request.query_params.get("recipient_email", None)
        code = request.query_params.get("code", None)
        pin = request.query_params.get("pin", None)
        if code and pin:
            if (
                Voucher.objects.exclude(in_cart=True)
                .filter(recipient_email=recipient_email, code=code, pin=pin)
                .exists()
            ):
                return Response({"is_voucher_code_valid_for_user": True})
        return Response({"is_voucher_code_valid_for_user": False})
