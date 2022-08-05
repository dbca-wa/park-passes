import logging

from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.retailers.models import RetailerGroupUser
from parkpasses.helpers import is_internal, is_retailer

logger = logging.getLogger(__name__)


class UserDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        user_data = {}
        # retailer_group = ''
        user_data["is_authenticated"] = request.user.is_authenticated
        if user_data["is_authenticated"]:
            emailuser = EmailUser.objects.get(id=request.user.id)
            user_data["user"] = {}
            user_data["user"]["email"] = emailuser.email
            user_data["user"]["first_name"] = emailuser.first_name
            user_data["user"]["last_name"] = emailuser.last_name
        if is_internal(request):
            user_data["authorisation_level"] = "internal"

        elif is_retailer(request):
            user_data["authorisation_level"] = "retailer"
            if RetailerGroupUser.objects.filter(emailuser__id=emailuser.id).exists():
                retailer_groups = (
                    RetailerGroupUser.objects.annotate()
                    .filter(emailuser__id=emailuser.id)
                    .values("retailer_group__id", "retailer_group__name")
                )
                retailer_groups_list = []
                user_data["user"]["retailer_groups"] = {}
                for retailer_group in retailer_groups:
                    retailer_groups_list.append(
                        {
                            "id": retailer_group["retailer_group__id"],
                            "name": retailer_group["retailer_group__name"],
                        }
                    )

                user_data["user"]["retailer_groups"] = retailer_groups_list

            logger.debug("retailer_groups" + str(list(retailer_groups)))
        else:
            user_data["authorisation_level"] = "external"

        return Response(user_data)
