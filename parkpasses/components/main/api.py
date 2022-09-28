import logging

from org_model_documents.api import DocumentCreateView, DocumentViewSet
from org_model_logs.api import (
    CreateCommunicationsLogEntry,
    EntryTypeList,
    UserActionList,
    UserActionViewSet,
)
from org_model_logs.serializers import EntryTypeSerializer

from parkpasses.components.main.serializers import (
    CommunicationsLogEntrySerializer,
    UserActionSerializer,
)
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


""" The following classes are overrideen here because the permission classes belong to park passes app
so can't be included in the org_model_documents or org_model_logs apps as it would break their independence"""


class DocumentCreateView(DocumentCreateView):
    permission_classes = [IsInternal]


class DocumentViewSet(DocumentViewSet):
    permission_classes = [IsInternal]


class EntryTypeList(EntryTypeList):
    serializer_class = EntryTypeSerializer
    permission_classes = [IsInternal]


class UserActionList(UserActionList):
    serializer_class = UserActionSerializer
    permission_classes = [IsInternal]


class UserActionViewSet(UserActionViewSet):
    permission_classes = [IsInternal]


class CreateCommunicationsLogEntry(CreateCommunicationsLogEntry):
    permission_classes = [IsInternal]

    def get_serializer_class(self):
        logger.debug("self.request.method = " + str(self.request.method))
        if "GET" == self.request.method:
            return CommunicationsLogEntrySerializer
        return super().get_serializer_class()
