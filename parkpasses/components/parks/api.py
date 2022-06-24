import logging

from rest_framework import viewsets

from parkpasses.components.parks.models import Postcode
from parkpasses.components.parks.serializers import PostcodeSerializer
from parkpasses.helpers import is_internal

logger = logging.getLogger(__name__)


class PostcodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on postcodes.
    """

    model = Postcode
    serializer_class = PostcodeSerializer

    def get_queryset(self):
        return Postcode.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        return False
