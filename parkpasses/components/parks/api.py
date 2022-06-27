import logging

from rest_framework import viewsets

from parkpasses.components.parks.models import LGA, Park, Postcode
from parkpasses.components.parks.serializers import (
    LGASerializer,
    ParkSerializer,
    PostcodeSerializer,
)
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


class ParkViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on parks / park groups.
    """

    model = Park
    serializer_class = ParkSerializer

    def get_queryset(self):
        return Park.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        return False


class LGAViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on LGAs.
    """

    model = LGA
    serializer_class = LGASerializer

    def get_queryset(self):
        return LGA.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        return False
