import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction
from parkpasses.components.vouchers.serializers import (
    InternalVoucherSerializer,
    InternalVoucherTransactionSerializer,
    VoucherSerializer,
    VoucherTransactionSerializer,
)
from parkpasses.helpers import is_internal

logger = logging.getLogger(__name__)


class VoucherViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on vouchers.
    """

    model = Voucher
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Voucher.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalVoucherSerializer
        else:
            return VoucherSerializer


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
