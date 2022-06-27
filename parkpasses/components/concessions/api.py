import logging

from rest_framework import viewsets

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

    def get_queryset(self):
        return Concession.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalConcessionSerializer
        else:
            return ConcessionSerializer

    def has_permission(self, request, view):
        return request.user.is_authenticated
