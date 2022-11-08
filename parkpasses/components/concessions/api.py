import logging

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from parkpasses.components.concessions.models import Concession
from parkpasses.components.concessions.serializers import (
    ExternalConcessionSerializer,
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
        return Concession.objects.all().order_by("display_order")

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalConcessionSerializer
        else:
            return ExternalConcessionSerializer

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_2_HOURS))
    def retrieve(self, request, pk=None):
        response = super().retrieve(request, pk=pk)
        return response

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_2_HOURS))
    def list(self, request, pk=None):
        response = super().list(request, pk=pk)
        return response
