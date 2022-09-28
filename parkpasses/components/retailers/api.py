import logging

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.components.retailers.serializers import RetailerGroupSerializer
from parkpasses.helpers import get_retailer_groups_for_user
from parkpasses.permissions import IsInternal, IsRetailer

logger = logging.getLogger(__name__)


class RetailerGroupsForUser(APIView):
    permission_classes = [IsRetailer]

    def get(self, request, format=None):
        retailer_groups = get_retailer_groups_for_user(request)
        serializer = RetailerGroupSerializer(retailer_groups, many=True)
        return Response(serializer.data)


class InternalRetailerGroupViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on reports.
    """

    model = RetailerGroup
    queryset = RetailerGroup.objects.all()
    permission_classes = [IsInternal]
    serializer_class = RetailerGroupSerializer
