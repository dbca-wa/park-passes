import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from parkpasses.components.help.models import HelpText
from parkpasses.components.help.serializers import (
    HelpTextSerializer,
    InternalHelpTextSerializer,
)
from parkpasses.helpers import is_internal

logger = logging.getLogger(__name__)


class HelpTextViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on help text.
    """

    model = HelpText
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return HelpText.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalHelpTextSerializer
        else:
            return HelpTextSerializer
