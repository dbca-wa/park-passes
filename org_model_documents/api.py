import logging

from rest_framework import generics, viewsets

from org_model_documents.models import Document
from org_model_documents.serializers import DocumentSerializer
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class DocumentCreateView(generics.CreateAPIView):
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        logger.debug("request.data ----> " + str(request.data))
        return super().post(request, *args, **kwargs)


class DocumentViewSet(viewsets.ModelViewSet):
    model = Document
    serializer_class = DocumentSerializer
    permission_classes = [IsInternal]
