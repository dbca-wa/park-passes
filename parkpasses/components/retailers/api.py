import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.retailers.serializers import RetailerGroupSerializer
from parkpasses.helpers import get_retailer_groups_for_user
from parkpasses.permissions import IsRetailer

logger = logging.getLogger(__name__)


class RetailerGroupsForUser(APIView):
    permission_classes = [IsRetailer]

    def get(self, request, format=None):
        retailer_groups = get_retailer_groups_for_user(request)
        serializer = RetailerGroupSerializer(retailer_groups, many=True)
        return Response(serializer.data)
