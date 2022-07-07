import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
            serializer.save(purchaser=self.request.user.id)
        else:
            serializer.save()

    def has_object_permission(self, request, view, obj):
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
