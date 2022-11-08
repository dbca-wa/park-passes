import logging

from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework.serializers import ValidationError
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from org_model_logs.models import CommunicationsLogEntry, EntryType, UserAction
from org_model_logs.serializers import (
    CommunicationsLogEntrySerializer,
    CreateCommunicationsLogEntrySerializer,
    EntryTypeSerializer,
    UserActionSerializer,
)
from org_model_logs.utils import BaseUserActionViewSet

logger = logging.getLogger(__name__)


class EntryTypeList(generics.ListAPIView):
    model = EntryType
    serializer_class = EntryTypeSerializer
    queryset = EntryType.objects.all()


class UserActionList(generics.ListAPIView):
    search_fields = ["what", "why"]
    model = UserAction
    serializer_class = UserActionSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (DatatablesFilterBackend,)
    ordering = ("-when",)

    def get_queryset(self):
        app_label = self.request.query_params.get("app_label", None)
        model = self.request.query_params.get("model", None)
        object_id = self.request.query_params.get("object_id", None)
        logger.info(
            "app_label: %s, model: %s, object_id: %s", app_label, model, object_id
        )
        if app_label and model and object_id:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                logger.info("content_type = " + str(content_type))
                return UserAction.objects.filter(
                    content_type=content_type, object_id=object_id
                )
        if app_label and model:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                return UserAction.objects.filter(content_type=content_type)
        if app_label:
            if ContentType.objects.filter(app_label=app_label).exists():
                content_types = ContentType.objects.filter(app_label=app_label)
                return UserAction.objects.filter(content_type__in=content_types)
        return UserAction.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserActionViewSet(BaseUserActionViewSet):
    model = UserAction
    serializer_class = UserActionSerializer
    queryset = UserAction.objects.all().order_by("-when")


class ListCreateCommunicationsLogEntry(generics.ListCreateAPIView):
    model = CommunicationsLogEntry
    filter_backends = (DatatablesFilterBackend,)
    pagination_class = DatatablesPageNumberPagination

    def get_serializer_class(self):
        if "POST" == self.request.method:
            return CreateCommunicationsLogEntrySerializer
        return CommunicationsLogEntrySerializer

    def get_queryset(self):
        app_label = self.request.query_params.get("app_label", None)
        model = self.request.query_params.get("model", None)
        object_id = self.request.query_params.get("object_id", None)
        if app_label and model and object_id:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                return CommunicationsLogEntry.objects.filter(
                    content_type=content_type, object_id=object_id
                )
        if app_label and model:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                return CommunicationsLogEntry.objects.filter(content_type=content_type)
        if app_label:
            if ContentType.objects.filter(app_label=app_label).exists():
                content_types = ContentType.objects.filter(app_label=app_label)
                return CommunicationsLogEntry.objects.filter(
                    content_type__in=content_types
                )
        return CommunicationsLogEntry.objects.all()

    def perform_create(self, serializer):
        app_label = serializer.validated_data.pop("app_label", None)
        model = serializer.validated_data.pop("model", None)
        logger.info("app_label: %s, model: %s", app_label, model)
        if not ContentType.objects.filter(app_label=app_label, model=model).exists():
            raise ValidationError(
                f"There is no content_type with app_label={app_label} and model={model}"
            )
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        logger.info("content_type = " + str(content_type))
        serializer.save(content_type=content_type, staff=self.request.user.id)
