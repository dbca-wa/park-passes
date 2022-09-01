import logging

from django.contrib.contenttypes.models import ContentType
from rest_framework import generics, viewsets
from rest_framework.filters import SearchFilter
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from org_model_logs.models import UserAction
from org_model_logs.serializers import UserActionSerializer
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class UserActionList(generics.ListAPIView):
    search_fields = ["what", "why"]
    model = UserAction
    serializer_class = UserActionSerializer
    permission_classes = [IsInternal]
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (
        SearchFilter,
        DatatablesFilterBackend,
    )

    def get_queryset(self):
        app_label = self.request.query_params.get("app_label", None)
        model = self.request.query_params.get("model", None)
        if ContentType.objects.filter(app_label=app_label, model=model).exists():
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            return UserAction.objects.filter(content_type=content_type)

        return UserAction.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserActionViewSet(viewsets.ModelViewSet):
    model = UserAction
    serializer_class = UserActionSerializer
    permission_classes = [IsInternal]
