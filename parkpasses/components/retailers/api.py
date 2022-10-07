import logging

from django.conf import settings
from django.db.models import Case, Count, Value, When
from django.http import Http404
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.retailers.emails import RetailerEmails
from parkpasses.components.retailers.models import (
    RetailerGroup,
    RetailerGroupInvite,
    RetailerGroupUser,
)
from parkpasses.components.retailers.serializers import (
    RetailerGroupInviteSerializer,
    RetailerGroupSerializer,
    RetailerGroupUserSerializer,
)
from parkpasses.helpers import get_retailer_groups_for_user
from parkpasses.permissions import IsInternal, IsRetailer

logger = logging.getLogger(__name__)


class RetailerGroupsForUser(APIView):
    permission_classes = [IsRetailer]

    def get(self, request, format=None):
        retailer_groups = get_retailer_groups_for_user(request)
        serializer = RetailerGroupSerializer(retailer_groups, many=True)
        return Response(serializer.data)


class RetailerGroupFilterBackend(DatatablesFilterBackend):
    """
    Custom Filters for Internal Pass Viewset
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        pass_type = request.GET.get("pass_type")
        processing_status = request.GET.get("processing_status")
        start_date_from = request.GET.get("start_date_from")
        start_date_to = request.GET.get("start_date_to")

        if pass_type:
            queryset = queryset.filter(option__pricing_window__pass_type__id=pass_type)

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

        if start_date_from:
            queryset = queryset.filter(date_start__gte=start_date_from)

        if start_date_to:
            queryset = queryset.filter(date_start__lte=start_date_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class InternalRetailerGroupViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on reports.
    """

    model = RetailerGroup
    queryset = RetailerGroup.objects.annotate(user_count=Count("retailergroupuser"))
    permission_classes = [IsInternal]
    serializer_class = RetailerGroupSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerGroupFilterBackend,)

    @action(methods=["GET"], detail=False, url_path="retailer-groups-excluding-dbca")
    def retailer_groups_excluding_dbca(self, request, *args, **kwargs):
        active_retailer_groups = self.get_queryset().exclude(
            name=settings.PARKPASSES_DEFAULT_SOLD_VIA
        )
        serializer = self.get_serializer(active_retailer_groups, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False, url_path="active-retailer-groups")
    def active_retailer_groups(self, request, *args, **kwargs):
        active_retailer_groups = (
            self.get_queryset()
            .filter(active=True)
            .exclude(name=settings.PARKPASSES_DEFAULT_SOLD_VIA)
        )
        serializer = self.get_serializer(active_retailer_groups, many=True)
        return Response(serializer.data)


class InternalRetailerGroupUserViewSet(viewsets.ModelViewSet):
    model = RetailerGroupUser
    queryset = RetailerGroupUser.objects.all()
    permission_classes = [IsInternal]
    serializer_class = RetailerGroupUserSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (DatatablesFilterBackend,)


class ExternalRetailerGroupInviteViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    model = RetailerGroupInvite
    permission_classes = [IsAuthenticated]
    serializer_class = RetailerGroupInviteSerializer
    pagination_class = DatatablesPageNumberPagination
    lookup_field = "uuid"

    def get_queryset(self):
        return RetailerGroupInvite.objects.filter(
            email=self.request.user.email
        ).annotate(
            user_count_for_retailer_group=Count("retailer_group__retailergroupuser")
        )

    @action(methods=["PUT"], detail=True, url_path="accept-retailer-group-user-invite")
    def accept_retailer_group_user_invite(self, request, *args, **kwargs):
        retailer_group_user_invite = self.get_object()
        if retailer_group_user_invite.user == request.user.id:
            retailer_group_user_invite.status = RetailerGroupInvite.USER_ACCEPTED
            retailer_group_user_invite.save()
            serializer = self.get_serializer(retailer_group_user_invite)
            return Response(serializer.data)
        raise Http404


class InternalRetailerGroupInviteViewSet(viewsets.ModelViewSet):
    model = RetailerGroupInvite
    queryset = (
        RetailerGroupInvite.objects.annotate(
            user_count_for_retailer_group=Count("retailer_group__retailergroupuser")
        )
        .exclude(status__in=[RetailerGroupInvite.APPROVED, RetailerGroupInvite.DENIED])
        .order_by(
            Case(
                When(status=RetailerGroupInvite.USER_ACCEPTED, then=Value(0)),
                When(status=RetailerGroupInvite.NEW, then=Value(1)),
                When(status=RetailerGroupInvite.SENT, then=Value(2)),
                When(status=RetailerGroupInvite.USER_LOGGED_IN, then=Value(3)),
            )
        )
    )
    permission_classes = [IsInternal]
    serializer_class = RetailerGroupInviteSerializer
    pagination_class = DatatablesPageNumberPagination

    @action(methods=["PUT"], detail=True, url_path="resend-retailer-group-user-invite")
    def resend_retailer_group_user_invite(self, request, *args, **kwargs):
        retailer_group_invite = self.get_object()
        if RetailerGroupInvite.NEW == retailer_group_invite.status:
            retailer_group_invite.save()
            serializer = self.get_serializer(retailer_group_invite)
            return Response(serializer.data)
        elif RetailerGroupInvite.SENT == retailer_group_invite.status:
            RetailerEmails.send_retailer_group_user_invite_notification_email(
                retailer_group_invite
            )
            serializer = self.get_serializer(retailer_group_invite)
            return Response(serializer.data)
        raise Http404

    @action(methods=["PUT"], detail=True, url_path="process-retailer-group-user-invite")
    def process_retailer_group_user_invite(self, request, *args, **kwargs):
        retailer_group_invite = self.get_object()
        logger.debug("retailer_group_invite = " + str(retailer_group_invite))
        logger.debug("request.data = " + str(request.data))
        if RetailerGroupInvite.USER_ACCEPTED != retailer_group_invite.status:
            raise Http404
        if not EmailUser.objects.filter(id=retailer_group_invite.user).exists():
            raise Http404
        email_user = EmailUser.objects.get(id=retailer_group_invite.user)
        if request.data["approved"]:
            if not RetailerGroupUser.objects.filter(
                retailer_group=retailer_group_invite.retailer_group,
                emailuser=email_user,
            ).exists():
                RetailerGroupUser.objects.create(
                    retailer_group=retailer_group_invite.retailer_group,
                    emailuser=email_user,
                    active=True,
                    is_admin=request.data["is_admin"],
                )
                retailer_group_invite.status = RetailerGroupInvite.APPROVED
        else:
            retailer_group_invite.status = RetailerGroupInvite.DENIED
        retailer_group_invite.save()
        serializer = self.get_serializer(retailer_group_invite)
        return Response(serializer.data)
