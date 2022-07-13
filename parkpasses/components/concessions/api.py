import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from parkpasses.components.concessions.models import Concession
from parkpasses.components.concessions.serializers import (
    ConcessionSerializer,
    InternalConcessionSerializer,
)
from parkpasses.helpers import is_internal

logger = logging.getLogger(__name__)


class ConcessionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on concessions.
    """

    model = Concession
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Concession.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalConcessionSerializer
        else:
            return ConcessionSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def retrieve(self, request, pk=None):
        response = super().retrieve(request, pk=pk)
        return response

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, pk=None):
        response = super().list(request, pk=pk)
        return response
