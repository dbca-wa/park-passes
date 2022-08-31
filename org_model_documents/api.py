import logging

from rest_framework import viewsets

from org_model_documents.models import Document
from org_model_documents.serializers import DocumentSerializer
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    model = Document
    serializer_class = DocumentSerializer
    permission_classes = [IsInternal]
