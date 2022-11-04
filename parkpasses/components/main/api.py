import logging

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from org_model_documents.api import DocumentCreateView, DocumentViewSet
from org_model_logs.api import EntryTypeList as BaseEntryTypeList
from org_model_logs.api import (
    ListCreateCommunicationsLogEntry as BaseListCreateCommunicationsLogEntry,
)
from org_model_logs.api import UserActionList as BaseUserActionList
from org_model_logs.api import UserActionViewSet as BaseUserActionViewSet
from org_model_logs.models import CommunicationsLogEntry
from org_model_logs.serializers import (
    CommunicationsLogEntrySerializer,
    EntryTypeSerializer,
)
from parkpasses.components.main.serializers import UserActionSerializer
from parkpasses.permissions import IsInternal, IsInternalAPIView

logger = logging.getLogger(__name__)


""" The following classes are overridden here because the permission classes belong to park passes app
so can't be included in the org_model_documents or org_model_logs apps as it would break their independence"""


class DocumentCreateView(DocumentCreateView):
    permission_classes = [IsInternalAPIView]


class DocumentViewSet(DocumentViewSet):
    permission_classes = [IsInternal]


class EntryTypeList(BaseEntryTypeList):
    serializer_class = EntryTypeSerializer
    permission_classes = [IsInternalAPIView]


class UserActionList(BaseUserActionList):
    serializer_class = UserActionSerializer
    permission_classes = [IsInternalAPIView]


class UserActionViewSet(BaseUserActionViewSet):
    permission_classes = [IsInternal]


class ListCreateCommunicationsLogEntry(BaseListCreateCommunicationsLogEntry):
    permission_classes = [IsInternalAPIView]

    def get_serializer_class(self):
        logger.debug("self.request.method = " + str(self.request.method))
        if "GET" == self.request.method:
            return CommunicationsLogEntrySerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        app_label = serializer.validated_data.pop("app_label", None)
        model = serializer.validated_data.pop("model", None)
        logger.debug(str(serializer.validated_data))
        if not ContentType.objects.filter(app_label=app_label, model=model).exists():
            raise ValidationError(
                f"There is no content_type with app_label={app_label} and model={model}"
            )
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        serializer.save(content_type=content_type, staff=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        comms_log_entry_content_type = ContentType.objects.get_for_model(
            CommunicationsLogEntry
        )
        extended_serializer = {
            "comms_log_entry_content_type": comms_log_entry_content_type.id
        }
        extended_serializer.update(serializer.data)
        return Response(
            extended_serializer, status=status.HTTP_201_CREATED, headers=headers
        )
