import logging

from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from org_model_logs.models import UserAction
from parkpasses.components.discount_codes.models import (
    DiscountCode,
    DiscountCodeBatch,
    DiscountCodeBatchComment,
    DiscountCodeBatchValidPassType,
    DiscountCodeBatchValidUser,
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

    def perform_create(self, serializer):
        logger.debug("self.request.data = " + str(self.request.data))
        new_discount_code_batch = serializer.save(created_by=self.request.user.id)
        content_type = ContentType.objects.get_for_model(new_discount_code_batch)
        reason = self.request.data.get("reason")
        valid_pass_types = self.request.data.get("valid_pass_types")

        for valid_pass_type in valid_pass_types:
            DiscountCodeBatchValidPassType.objects.create(
                discount_code_batch_id=new_discount_code_batch.id,
                pass_type_id=valid_pass_type,
            )
        valid_users = self.request.data.get("valid_users")

        for valid_user in valid_users:
            DiscountCodeBatchValidUser.objects.create(
                discount_code_batch_id=new_discount_code_batch.id, user=valid_user
            )

        logger.debug("reason = " + str(reason))
        user_action = UserAction.objects.log_action(
            object_id=new_discount_code_batch.id,
            content_type=content_type,
            who=self.request.user.id,
            what="Create Discount Code Batch " + str(new_discount_code_batch.id),
            why=reason,
        )
        user_action.save()


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
