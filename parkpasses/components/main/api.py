import logging

from org_model_documents.api import DocumentCreateView, DocumentViewSet
from org_model_logs.api import UserActionList, UserActionViewSet
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class DocumentCreateView(DocumentCreateView):
    """The permission classes belong to park passes so can't be included in the org_model_documents app"""

    permission_classes = [IsInternal]


class DocumentViewSet(DocumentViewSet):
    """The permission classes belong to park passes so can't be included in the org_model_documents app"""

    permission_classes = [IsInternal]


class UserActionList(UserActionList):
    """The permission classes belong to park passes so can't be included in the org_model_documents app"""

    permission_classes = [IsInternal]


class UserActionViewSet(UserActionViewSet):
    """The permission classes belong to park passes so can't be included in the org_model_documents app"""

    permission_classes = [IsInternal]
