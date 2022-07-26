import logging

from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.parks.models import LGA, Park, ParkGroup, Postcode
from parkpasses.components.parks.serializers import (
    ExternalParkGroupSerializer,
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


class ValidatePostcodeView(APIView):
    def get(self, request, format=None):
        postcode = request.query_params.get("postcode", None)
        if postcode:
            if Postcode.objects.filter(postcode=postcode).exists():
                return Response({"is_postcode_valid": True})
        return Response({"is_postcode_valid": False})


class ParkGroupsForPostcodeView(ListAPIView):
    serializer_class = ExternalParkGroupSerializer

    def get_queryset(self):
        queryset = ParkGroup.objects.none()
        postcode = self.request.query_params.get("postcode")
        if Postcode.objects.filter(postcode=postcode).exists():
            queryset = ParkGroup.get_park_groups_by_postcode(postcode=postcode)
        return queryset
