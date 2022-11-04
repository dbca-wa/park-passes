import logging

from django.http import FileResponse, Http404
from rest_framework import generics, viewsets
from rest_framework.decorators import action

from org_model_documents.models import Document
from org_model_documents.serializers import DocumentSerializer

logger = logging.getLogger(__name__)


class DocumentCreateView(generics.CreateAPIView):
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        logger.debug("request.data ----> " + str(request.data))
        return super().post(request, *args, **kwargs)


class DocumentViewSet(viewsets.ModelViewSet):
    model = Document
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()

    @action(methods=["GET"], detail=True, url_path="retrieve-document")
    def retrieve_document(self, request, *args, **kwargs):
        document = self.get_object()
        if document._file:
            return FileResponse(document._file)
        raise Http404
