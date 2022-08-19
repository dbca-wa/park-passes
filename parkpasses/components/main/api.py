import logging

from rest_framework import viewsets
from rest_framework.response import Response

from parkpasses.components.main.models import MapLayer, Question, RequiredDocument
from parkpasses.components.main.serializers import (
    MapLayerSerializer,
    QuestionSerializer,
    RequiredDocumentSerializer,
)
from parkpasses.helpers import is_customer, is_internal

logger = logging.getLogger("payment_checkout")


class RequiredDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class MapLayerViewSet(viewsets.ModelViewSet):
    queryset = MapLayer.objects.none()
    serializer_class = MapLayerSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return MapLayer.objects.filter(option_for_internal=True)
        elif is_customer(self.request):
            return MapLayer.objects.filter(option_for_external=True)
        return MapLayer.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
