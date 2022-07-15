import logging

from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.helpers import is_internal, is_retailer

logger = logging.getLogger(__name__)


class UserDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        user_data = {}
        # retailer_group = ''
        user_data["isAuthenticated"] = request.user.is_authenticated
        if user_data["isAuthenticated"]:
            emailuser = EmailUser.objects.get(id=request.user.id)
            user_data["user"] = {}
            user_data["user"]["email"] = emailuser.email
            user_data["user"]["first_name"] = emailuser.first_name
            user_data["user"]["last_name"] = emailuser.last_name
        if is_internal(request):
            user_data["authorisationLevel"] = "internal"
        elif is_retailer(request):
            user_data["authorisationLevel"] = "retailer"
            # Todo: At some stage we will need to add the retailer group
            # retailer_group =
        else:
            user_data["authorisationLevel"] = "external"

        return Response(user_data)
