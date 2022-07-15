import logging

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.helpers import is_internal, is_retailer

logger = logging.getLogger(__name__)


class UserDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        # retailer_group = ''
        if is_internal(request):
            authorisation_level = "internal"
        elif is_retailer(request):
            authorisation_level = "retailer"
            # Todo: At some stage we will need to add the retailer group
            # retailer_group =
        else:
            authorisation_level = "external"

        return Response(
            {
                "isAuthenticated": request.user.is_authenticated,
                "authorisationLevel": authorisation_level,
                # "authorisationLevel": authorisation_level,
            }
        )
