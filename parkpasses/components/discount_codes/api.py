import logging

from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.discount_codes.models import (
    DiscountCode,
    DiscountCodeBatch,
    DiscountCodeBatchComment,
)
from parkpasses.components.discount_codes.serializers import (
    InternalDiscountCodeBatchCommentSerializer,
    InternalDiscountCodeBatchSerializer,
    InternalDiscountCodeSerializer,
)
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class DiscountCodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on discount codes.
    """

    model = DiscountCode
    queryset = DiscountCode.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InternalDiscountCodeSerializer


class InternalDiscountCodeBatchViewSet(viewsets.ModelViewSet):
    model = DiscountCodeBatch
    pagination_class = DatatablesPageNumberPagination
    queryset = DiscountCodeBatch.objects.all()
    permission_classes = [IsInternal]
    serializer_class = InternalDiscountCodeBatchSerializer
    filter_backends = (
        SearchFilter,
        DatatablesFilterBackend,
    )
    filterset_fields = [
        "times_each_code_can_be_used",
    ]


class DiscountCodeBatchCommentViewSet(viewsets.ModelViewSet):
    model = DiscountCodeBatchComment
    queryset = DiscountCodeBatchComment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InternalDiscountCodeBatchCommentSerializer


class ValidateDiscountCodeView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, format=None):
        code = request.query_params.get("code", None)
        if code:
            if DiscountCode.objects.filter(remaining_uses__gt=0, code=code).exists():
                return Response({"is_discount_code_valid": True})
        return Response({"is_discount_code_valid": False})
