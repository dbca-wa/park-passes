import logging

from django.db.models import CharField, Value
from django.db.models.functions import Concat
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from parkpasses.permissions import IsInternal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.retailers.models import RetailerGroup, RetailerGroupUser
from parkpasses.components.users.serializers import BasicEmailUserSerializer
from parkpasses.helpers import (
    is_internal,
    is_parkpasses_discount_code_percentage_user,
    is_retailer,
)

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
            user_data["user"]["can_create_percentage_discounts"] = (
                is_parkpasses_discount_code_percentage_user(request)
            )

        elif is_retailer(request):
            user_data["authorisation_level"] = "retailer"
            if RetailerGroupUser.objects.filter(emailuser__id=emailuser.id).exists():
                retailer_group_user_ids = (
                    RetailerGroupUser.objects.annotate()
                    .filter(emailuser__id=emailuser.id)
                    .values_list("retailer_group__id", flat=True)
                )
                retailer_groups_list = []
                user_data["user"]["retailer_groups"] = {}
                retailer_groups = RetailerGroup.objects.filter(
                    id__in=[retailer_group_user_ids]
                )
                for retailer_group in retailer_groups:
                    retailer_groups_list.append(
                        {
                            "id": retailer_group.id,
                            "name": retailer_group.organisation["organisation_name"],
                            "internal": retailer_group.is_internal_retailer,
                        }
                    )

                user_data["user"]["retailer_groups"] = retailer_groups_list

        else:
            user_data["authorisation_level"] = "external"

        return Response(user_data)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = BasicEmailUserSerializer
    permission_classes = [IsInternal]

    def get_queryset(self):
        return EmailUser.objects.all()

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def get_customers(self, request, *args, **kwargs):
        search_term = request.GET.get("term", "")
        customers = (
            self.get_queryset()
            .filter(is_staff=False)
            .annotate(
                search_term=Concat(
                    "first_name",
                    Value(" "),
                    "last_name",
                    Value(" "),
                    "email",
                    output_field=CharField(),
                )
            )
        )
        customers = customers.filter(search_term__icontains=search_term).values(
            "id", "email", "first_name", "last_name"
        )[:10]
        data_transform = [
            {
                "id": customer["id"],
                "text": customer["first_name"]
                + " "
                + customer["last_name"]
                + " ("
                + customer["email"]
                + ")",
            }
            for customer in customers
        ]
        return Response({"results": data_transform})
