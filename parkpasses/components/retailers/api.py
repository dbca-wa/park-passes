import logging

from django.conf import settings
from django.db.models import Case, Count, Q, Value, When
from django.http import Http404
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.main.api import (
    CustomDatatablesListMixin,
    CustomDatatablesRenderer,
)
from parkpasses.components.retailers.emails import RetailerEmails
from parkpasses.components.retailers.models import (
    District,
    RetailerGroup,
    RetailerGroupInvite,
    RetailerGroupUser,
)
from parkpasses.components.retailers.serializers import (
    DistrictSerializer,
    InternalRetailerGroupInviteSerializer,
    RetailerGroupSerializer,
    RetailerGroupUserSerializer,
    RetailerRetailerGroupInviteSerializer,
)
from parkpasses.helpers import (
    delete_sessions_by_emailuser_id,
    get_retailer_groups_for_user,
)
from parkpasses.permissions import IsInternal, IsRetailer, IsRetailerAdmin

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
    A ViewSet for internal users to perform actions on retailer groups.
    """

    model = RetailerGroup
    queryset = RetailerGroup.objects.annotate(user_count=Count("retailer_group_users"))
    permission_classes = [IsInternal]
    serializer_class = RetailerGroupSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerGroupFilterBackend,)

    @action(methods=["GET"], detail=False, url_path="retailer-groups-excluding-dbca")
    def retailer_groups_excluding_dbca(self, request, *args, **kwargs):
        active_retailer_groups = self.get_queryset().exclude(
            ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
        )
        serializer = self.get_serializer(active_retailer_groups, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False, url_path="active-retailer-groups")
    def active_retailer_groups(self, request, *args, **kwargs):
        active_retailer_groups = (
            self.get_queryset()
            .filter(active=True)
            .exclude(
                ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
            )
        )
        serializer = self.get_serializer(active_retailer_groups, many=True)
        return Response(serializer.data)


class RetailerGroupUserFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        is_active = request.GET.get("is_active")
        datetime_created_from = request.GET.get("datetime_created_from")
        datetime_created_to = request.GET.get("datetime_created_to")

        if is_active:
            queryset = queryset.filter(active=is_active)

        if datetime_created_from:
            queryset = queryset.filter(datetime_created__gte=datetime_created_from)

        if datetime_created_to:
            queryset = queryset.filter(datetime_created__lte=datetime_created_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class RetailerRetailerGroupUserViewSet(
    CustomDatatablesListMixin, viewsets.ModelViewSet
):
    model = RetailerGroupUser
    queryset = RetailerGroupUser.objects.all()
    permission_classes = [IsRetailerAdmin]
    serializer_class = RetailerGroupUserSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerGroupUserFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    def get_queryset(self):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id")
            return RetailerGroupUser.objects.filter(
                retailer_group__in=list(retailer_groups)
            )
        return RetailerGroupUser.objects.none()

    @action(methods=["PUT"], detail=True, url_path="toggle-active")
    def toggle_active(self, request, *args, **kwargs):
        retailer_group_user = self.get_object()
        retailer_group_user.active = not retailer_group_user.active
        retailer_group_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RetailerGroupUserFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        retailer_group = request.GET.get("retailer_group")
        is_admin = request.GET.get("is_admin")
        datetime_created_from = request.GET.get("datetime_created_from")
        datetime_created_to = request.GET.get("datetime_created_to")

        if retailer_group:
            queryset = queryset.filter(retailer_group_id=retailer_group)

        if is_admin:
            queryset = queryset.filter(is_admin=is_admin)

        if datetime_created_from:
            queryset = queryset.filter(datetime_created__gte=datetime_created_from)

        if datetime_created_to:
            queryset = queryset.filter(datetime_created__lte=datetime_created_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class InternalRetailerGroupUserViewSet(
    CustomDatatablesListMixin, viewsets.ModelViewSet
):
    model = RetailerGroupUser
    retailer_group_admin_user_count = Count(
        "retailer_group",
        filter=Q(retailer_group__retailer_group_users__is_admin=True),
    )
    queryset = RetailerGroupUser.objects.annotate(
        retailer_group_admin_user_count=retailer_group_admin_user_count
    )
    permission_classes = [IsInternal]
    serializer_class = RetailerGroupUserSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerGroupUserFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    @action(methods=["PUT"], detail=True, url_path="toggle-active")
    def toggle_active(self, request, *args, **kwargs):
        retailer_group_user = self.get_object()
        retailer_group_user.active = not retailer_group_user.active
        retailer_group_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["PUT"], detail=True, url_path="toggle-is-admin")
    def toggle_is_admin(self, request, *args, **kwargs):
        retailer_group_user = self.get_object()
        retailer_group_user.is_admin = not retailer_group_user.is_admin
        retailer_group_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExternalRetailerGroupInviteViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    model = RetailerGroupInvite
    permission_classes = [IsAuthenticated]
    serializer_class = InternalRetailerGroupInviteSerializer
    pagination_class = DatatablesPageNumberPagination
    lookup_field = "uuid"

    def get_queryset(self):
        return RetailerGroupInvite.objects.filter(
            email=self.request.user.email
        ).annotate(
            user_count_for_retailer_group=Count("retailer_group__retailer_group_users")
        )

    @action(methods=["PUT"], detail=True, url_path="accept-retailer-group-user-invite")
    def accept_retailer_group_user_invite(self, request, *args, **kwargs):
        retailer_group_user_invite = self.get_object()
        if retailer_group_user_invite.user == request.user.id:
            email_user = EmailUser.objects.get(id=retailer_group_user_invite.user)
            if (
                RetailerGroupInvite.INTERNAL_USER
                == retailer_group_user_invite.initiated_by
            ):
                retailer_group_user_invite.status = RetailerGroupInvite.USER_ACCEPTED
            if (
                RetailerGroupInvite.RETAILER_USER
                == retailer_group_user_invite.initiated_by
            ):
                # Since retailers can only add users to their own retailer group and cannot create
                # admins we bypass the additional steps and just approve them when they accept their invite
                RetailerGroupUser.objects.create(
                    retailer_group=retailer_group_user_invite.retailer_group,
                    emailuser=email_user,
                    active=True,
                )
                retailer_group_user_invite.status = RetailerGroupInvite.APPROVED
                # Log the user out so that they must log in again and we can
                # add the retailer group name and id to their session
                delete_sessions_by_emailuser_id(email_user.id)

            retailer_group_user_invite.save()
            serializer = self.get_serializer(retailer_group_user_invite)
            return Response(serializer.data)
        raise Http404


class RetailerGroupUserInviteFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        retailer_group = request.GET.get("retailer_group")
        status = request.GET.get("status")
        datetime_created_from = request.GET.get("datetime_created_from")
        datetime_created_to = request.GET.get("datetime_created_to")

        if retailer_group:
            queryset = queryset.filter(retailer_group_id=retailer_group)

        if status:
            queryset = queryset.filter(status=status)

        if datetime_created_from:
            queryset = queryset.filter(datetime_created__gte=datetime_created_from)

        if datetime_created_to:
            queryset = queryset.filter(datetime_created__lte=datetime_created_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class InternalRetailerGroupInviteViewSet(
    CustomDatatablesListMixin, viewsets.ModelViewSet
):
    model = RetailerGroupInvite
    queryset = (
        RetailerGroupInvite.objects.annotate(
            user_count_for_retailer_group=Count("retailer_group__retailer_group_users")
        )
        .exclude(status__in=[RetailerGroupInvite.APPROVED, RetailerGroupInvite.DENIED])
        .filter(initiated_by=RetailerGroupInvite.INTERNAL_USER)
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
    serializer_class = InternalRetailerGroupInviteSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerGroupUserInviteFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    @action(methods=["PUT"], detail=True, url_path="resend-retailer-group-user-invite")
    def resend_retailer_group_user_invite(self, request, *args, **kwargs):
        retailer_group_user_invite = self.get_object()
        if RetailerGroupInvite.NEW == retailer_group_user_invite.status:
            retailer_group_user_invite.save()
            serializer = self.get_serializer(retailer_group_user_invite)
            return Response(serializer.data)
        elif RetailerGroupInvite.SENT == retailer_group_user_invite.status:
            RetailerEmails.send_retailer_group_user_invite_notification_email(
                retailer_group_user_invite
            )
            serializer = self.get_serializer(retailer_group_user_invite)
            return Response(serializer.data)
        raise Http404

    @action(methods=["PUT"], detail=True, url_path="process-retailer-group-user-invite")
    def process_retailer_group_user_invite(self, request, *args, **kwargs):
        retailer_group_user_invite = self.get_object()
        if RetailerGroupInvite.USER_ACCEPTED != retailer_group_user_invite.status:
            raise Http404
        if not EmailUser.objects.filter(id=retailer_group_user_invite.user).exists():
            raise Http404
        email_user = EmailUser.objects.get(id=retailer_group_user_invite.user)
        if request.data["approved"]:
            if not RetailerGroupUser.objects.filter(
                retailer_group=retailer_group_user_invite.retailer_group,
                emailuser=email_user,
            ).exists():
                RetailerGroupUser.objects.create(
                    retailer_group=retailer_group_user_invite.retailer_group,
                    emailuser=email_user,
                    active=True,
                    is_admin=request.data["is_admin"],
                )
                retailer_group_user_invite.status = RetailerGroupInvite.APPROVED
                # Log the user out so that they must log in again and we can
                # add the retailer group name and id to their session
                delete_sessions_by_emailuser_id(email_user.id)

        else:
            retailer_group_user_invite.status = RetailerGroupInvite.DENIED
        retailer_group_user_invite.save()
        serializer = self.get_serializer(retailer_group_user_invite)
        return Response(serializer.data)


class RetailerRetailerGroupInviteViewSet(
    CustomDatatablesListMixin, viewsets.ModelViewSet
):
    model = RetailerGroupInvite
    permission_classes = [IsRetailerAdmin]
    serializer_class = RetailerRetailerGroupInviteSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerGroupUserInviteFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    def perform_create(self, serializer):
        serializer.save(initiated_by=RetailerGroupInvite.RETAILER_USER)

    def get_queryset(self):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id")
            return (
                RetailerGroupInvite.objects.annotate(
                    user_count_for_retailer_group=Count(
                        "retailer_group__retailer_group_users"
                    )
                )
                .exclude(
                    status__in=[
                        RetailerGroupInvite.APPROVED,
                        RetailerGroupInvite.DENIED,
                        RetailerGroupInvite.USER_ACCEPTED,
                        RetailerGroupInvite.USER_LOGGED_IN,
                    ]
                )
                .filter(
                    retailer_group__in=list(retailer_groups),
                    initiated_by=RetailerGroupInvite.RETAILER_USER,
                )
                .order_by(
                    Case(
                        When(status=RetailerGroupInvite.NEW, then=Value(1)),
                        When(status=RetailerGroupInvite.SENT, then=Value(2)),
                    )
                )
            )
        return RetailerGroupUser.objects.none()


class InternalDistrictViewSet(viewsets.ModelViewSet):
    model = District
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
