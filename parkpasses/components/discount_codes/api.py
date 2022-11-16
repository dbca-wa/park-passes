import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from org_model_logs.models import UserAction
from org_model_logs.utils import BaseUserActionViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

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
    InternalDiscountCodeXlsxSerializer,
)
from parkpasses.components.main.api import (
    CustomDatatablesListMixin,
    CustomDatatablesRenderer,
)
from parkpasses.components.main.serializers import UserActionSerializer
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class DiscountCodeXlsxViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for performing actions on discount codes.
    """

    model = DiscountCode
    permission_classes = [IsInternal]
    serializer_class = InternalDiscountCodeXlsxSerializer
    renderer_classes = (XLSXRenderer,)
    paginator = None

    def get_discount_code_batch(self):
        discount_code_batch_id = self.kwargs["discount_code_batch_id"]
        if DiscountCodeBatch.objects.filter(id=discount_code_batch_id).exists():
            return DiscountCodeBatch.objects.get(id=discount_code_batch_id)
        return None  # raise object does not exist exception?

    def get_queryset(self):
        discount_code_batch = self.get_discount_code_batch()
        return DiscountCode.objects.filter(
            discount_code_batch_id=discount_code_batch.id
        )

    def get_filename(self, request, *args, **kwargs):
        discount_code_batch = self.get_discount_code_batch()
        discount_code_batch_number = discount_code_batch.discount_code_batch_number
        discount_codes_count = len(list(self.get_queryset()))
        return f"discount_code_batch_{discount_code_batch_number}_{discount_codes_count}_codes.xlsx"


class DiscountCodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on discount codes.
    """

    model = DiscountCode
    queryset = DiscountCode.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InternalDiscountCodeSerializer


class DiscountCodeBatchFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        status = request.GET.get("status")

        datetime_start_from = request.GET.get("datetime_start_from")
        datetime_start_to = request.GET.get("datetime_start_to")

        datetime_expiry_from = request.GET.get("datetime_expiry_from")
        datetime_expiry_to = request.GET.get("datetime_expiry_to")

        if "Expired" == status:
            queryset = queryset.filter(datetime_expiry__lte=timezone.now())
        if "Current" == status:
            queryset = queryset.filter(
                datetime_start__lte=timezone.now(), datetime_expiry__gte=timezone.now()
            )
        if "Future" == status:
            queryset = queryset.filter(datetime_start__gt=timezone.now())

        if datetime_start_from:
            queryset = queryset.filter(datetime_start__gte=datetime_start_from)

        if datetime_start_to:
            queryset = queryset.filter(datetime_start__lte=datetime_start_to)

        if datetime_expiry_from:
            queryset = queryset.filter(datetime_expiry__gte=datetime_expiry_from)

        if datetime_expiry_to:
            queryset = queryset.filter(datetime_expiry__lte=datetime_expiry_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class InternalDiscountCodeBatchViewSet(
    CustomDatatablesListMixin, BaseUserActionViewSet
):
    model = DiscountCodeBatch
    pagination_class = DatatablesPageNumberPagination
    queryset = DiscountCodeBatch.objects.all()
    permission_classes = [IsInternal]
    serializer_class = InternalDiscountCodeBatchSerializer
    filter_backends = (DiscountCodeBatchFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    def get_user_action_serializer_class(self):
        return UserActionSerializer

    def perform_create(self, serializer):
        new_discount_code_batch = serializer.save(created_by=self.request.user.id)

        valid_pass_types = self.request.data.get("valid_pass_types")
        if valid_pass_types:
            for valid_pass_type in valid_pass_types:
                DiscountCodeBatchValidPassType.objects.create(
                    discount_code_batch_id=new_discount_code_batch.id,
                    pass_type_id=valid_pass_type,
                )

        valid_users = self.request.data.get("valid_users")
        if valid_users:
            for valid_user in valid_users:
                DiscountCodeBatchValidUser.objects.create(
                    discount_code_batch_id=new_discount_code_batch.id, user=valid_user
                )

    def perform_update(self, serializer):
        updated_discount_code_batch = serializer.save()

        valid_pass_types = self.request.data.get("valid_pass_types")
        if valid_pass_types:
            # Delete any pass types that are no longer valid
            if (
                DiscountCodeBatchValidPassType.objects.filter(
                    discount_code_batch_id=updated_discount_code_batch.id
                )
                .exclude(pass_type_id__in=valid_pass_types)
                .exists()
            ):
                DiscountCodeBatchValidPassType.objects.filter(
                    discount_code_batch_id=updated_discount_code_batch.id
                ).exclude(pass_type_id__in=valid_pass_types).delete()

            # Create any newly added pass types that are valid
            for valid_pass_type in valid_pass_types:
                if not DiscountCodeBatchValidPassType.objects.filter(
                    discount_code_batch_id=updated_discount_code_batch.id,
                    pass_type_id=valid_pass_type,
                ).exists():
                    DiscountCodeBatchValidPassType.objects.create(
                        discount_code_batch_id=updated_discount_code_batch.id,
                        pass_type_id=valid_pass_type,
                    )

        valid_users = self.request.data.get("valid_users")
        if valid_users:
            # Delete any users that are no longer valid
            if (
                DiscountCodeBatchValidUser.objects.filter(
                    discount_code_batch_id=updated_discount_code_batch.id
                )
                .exclude(user__in=valid_users)
                .exists()
            ):
                DiscountCodeBatchValidUser.objects.filter(
                    discount_code_batch_id=updated_discount_code_batch.id
                ).exclude(user__in=valid_users).delete()

            # Create any newly added users that are valid
            for valid_user in valid_users:
                if not DiscountCodeBatchValidUser.objects.filter(
                    discount_code_batch_id=updated_discount_code_batch.id,
                    user=valid_user,
                ).exists():
                    DiscountCodeBatchValidUser.objects.create(
                        discount_code_batch_id=updated_discount_code_batch.id,
                        user=valid_user,
                    )

    @action(methods=["PUT"], detail=True, url_path="invalidate-discount-code-batch")
    def invalidate_discount_code_batch(self, request, *args, **kwargs):
        discount_code_batch = self.get_object()
        discount_code_batch.invalidated = True
        discount_code_batch.save()
        user_action = settings.ACTION_INVALIDATE
        content_type = ContentType.objects.get_for_model(DiscountCodeBatch)
        user_action = UserAction.objects.log_action(
            object_id=discount_code_batch.id,
            content_type=content_type,
            who=request.user.id,
            what=user_action.format(
                DiscountCodeBatch._meta.model.__name__, discount_code_batch.id
            ),
            why=request.data["invalidation_reason"],
        )
        serializer = {"user_action": UserActionSerializer(user_action).data}
        return Response(serializer, status=status.HTTP_201_CREATED)


class DiscountCodeBatchCommentViewSet(viewsets.ModelViewSet):
    model = DiscountCodeBatchComment
    queryset = DiscountCodeBatchComment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InternalDiscountCodeBatchCommentSerializer


class ValidateDiscountCodeView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, format=None):
        code = request.query_params.get("code", None)
        pass_type_id = request.query_params.get("pass_type_id", None)
        email = request.query_params.get("email", None)

        if code and 8 == len(code) and email and pass_type_id:
            if DiscountCode.objects.filter(
                invalidated=False,
                code=code,
                discount_code_batch__datetime_start__lte=timezone.now(),
                discount_code_batch__datetime_expiry__gte=timezone.now(),
            ).exists():
                discount_code = DiscountCode.objects.get(code=code)
                if (
                    discount_code.remaining_uses == settings.UNLIMITED_USES_TEXT
                    or 0 < discount_code.remaining_uses
                ):
                    if discount_code.is_valid_for_pass_type(pass_type_id):
                        if discount_code.is_valid_for_email(email):
                            return Response(
                                {
                                    "is_discount_code_valid": True,
                                    "discount_type": discount_code.discount_type,
                                    "discount": discount_code.discount,
                                }
                            )

        return Response({"is_discount_code_valid": False})
