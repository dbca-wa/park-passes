import logging

from org_model_documents.api import DocumentCreateView, DocumentViewSet

from org_model_logs.api import (
    CreateCommunicationsLogEntry as BaseCreateCommunicationsLogEntry,
)
from org_model_logs.api import EntryTypeList as BaseEntryTypeList
from org_model_logs.api import UserActionList as BaseUserActionList
from org_model_logs.api import UserActionViewSet as BaseUserActionViewSet
from org_model_logs.serializers import EntryTypeSerializer
from parkpasses.components.main.serializers import (
    CommunicationsLogEntrySerializer,
    UserActionSerializer,
)
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


class CreateCommunicationsLogEntry(BaseCreateCommunicationsLogEntry):
    permission_classes = [IsInternalAPIView]

    def get_serializer_class(self):
        logger.debug("self.request.method = " + str(self.request.method))
        if "GET" == self.request.method:
            return CommunicationsLogEntrySerializer
        return super().get_serializer_class()
