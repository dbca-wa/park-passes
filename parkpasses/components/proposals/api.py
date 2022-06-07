import traceback
import os
import base64
import geojson
import json
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import (
    action as detail_route,
    renderer_classes,
    parser_classes,
)
from rest_framework.decorators import action as list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    BasePermission,
)
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from django.core.cache import cache
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, Address
from ledger_api_client.country_models import Country
from datetime import datetime, timedelta, date
from parkpasses.components.proposals.utils import (
    save_proponent_data,
)
from parkpasses.components.proposals.models import (
    ProposalUserAction,
)
from parkpasses.settings import (
    APPLICATION_TYPES,
)
from parkpasses.components.main.utils import check_db_connection
from parkpasses.components.main.decorators import basic_exception_handler

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from parkpasses.components.main.models import (
    Document,
    ApplicationType,
    RequiredDocument,
)
from parkpasses.components.proposals.models import (
    ProposalType,
    Proposal,
)
from parkpasses.components.proposals.serializers import (
    ProposalTypeSerializer,
    ProposalUserActionSerializer,
    ProposalLogEntrySerializer,
    ListProposalSerializer,
    ProposalSerializer,
    InternalProposalSerializer,
)
from parkpasses.components.main.process_document import (
    process_generic_document,
)

from parkpasses.helpers import is_customer, is_internal, is_assessor, is_approver
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer
from rest_framework.filters import BaseFilterBackend

# import reversion
# from reversion.models import Version

import logging

logger = logging.getLogger("parkpasses")


class GetApplicationTypeDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        for_filter = request.query_params.get("for_filter", "")
        for_filter = True if for_filter == "true" else False
        cache_data_name = (
            "application_type_dict_for_filter"
            if for_filter
            else "application_type_dict"
        )

        data = cache.get(cache_data_name)
        if not data:
            if for_filter:
                cache.set(
                    cache_data_name,
                    [
                        {"id": app_type[0], "text": app_type[1]}
                        for app_type in settings.APPLICATION_TYPES
                    ],
                    settings.LOV_CACHE_TIMEOUT,
                )
            else:
                cache.set(
                    cache_data_name,
                    [
                        {"code": app_type[0], "description": app_type[1]}
                        for app_type in settings.APPLICATION_TYPES
                        if app_type[0] == "registration_of_interest"
                    ],
                    settings.LOV_CACHE_TIMEOUT,
                )
            data = cache.get(cache_data_name)
        return Response(data)


class GetApplicationTypeDescriptions(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = cache.get("application_type_descriptions")
        if not data:
            cache.set(
                "application_type_descriptions",
                [app_type[1] for app_type in settings.APPLICATION_TYPES],
                settings.LOV_CACHE_TIMEOUT,
            )
            data = cache.get("application_type_descriptions")
        return Response(data)


class GetApplicationStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = {}

        for_filter = request.query_params.get("for_filter", "")
        for_filter = True if for_filter == "true" else False

        if for_filter:
            cache_name = ("application_internal_statuses_dict_for_filter",)
            cache.set(
                cache_name,
                [
                    {"id": i[0], "text": i[1]}
                    for i in Proposal.PROCESSING_STATUS_CHOICES
                ],
                settings.LOV_CACHE_TIMEOUT,
            )
            data = cache.get(cache_name)
            return Response(data)
        else:
            if not cache.get("application_internal_statuses_dict") or not cache.get(
                "application_external_statuses_dict"
            ):
                cache.set(
                    "application_internal_statuses_dict",
                    [
                        {"code": i[0], "description": i[1]}
                        for i in Proposal.PROCESSING_STATUS_CHOICES
                    ],
                    settings.LOV_CACHE_TIMEOUT,
                )
                cache.set(
                    "application_external_statuses_dict",
                    [
                        {"code": i[0], "description": i[1]}
                        for i in Proposal.PROCESSING_STATUS_CHOICES
                    ],
                    settings.LOV_CACHE_TIMEOUT,
                )
            data["external_statuses"] = cache.get("application_external_statuses_dict")
            data["internal_statuses"] = cache.get("application_internal_statuses_dict")
            return Response(data)


class GetProposalType(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        _type = ProposalType.objects.first()
        if _type:
            serializer = ProposalTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "There is currently no application type."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetEmptyList(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        return Response([])


class ProposalFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        filter_lodged_from = request.GET.get("filter_lodged_from")
        filter_lodged_to = request.GET.get("filter_lodged_to")
        filter_application_type = (
            request.GET.get("filter_application_type")
            if request.GET.get("filter_application_type") != "all"
            else ""
        )
        filter_application_status = (
            request.GET.get("filter_application_status")
            if request.GET.get("filter_application_status") != "all"
            else ""
        )

        if queryset.model is Proposal:
            if filter_lodged_from:
                filter_lodged_from = datetime.strptime(filter_lodged_from, "%Y-%m-%d")
                queryset = queryset.filter(lodgement_date__gte=filter_lodged_from)
            if filter_lodged_to:
                filter_lodged_to = datetime.strptime(filter_lodged_to, "%Y-%m-%d")
                queryset = queryset.filter(lodgement_date__lte=filter_lodged_to)
            if filter_application_type:
                application_type = ApplicationType.get_application_type_by_name(
                    filter_application_type
                )
                queryset = queryset.filter(application_type=application_type)
            if filter_application_status:
                queryset = queryset.filter(processing_status=filter_application_status)
        elif queryset.model is Compliance:
            if filter_lodged_from:
                queryset = queryset.filter(due_date__gte=filter_lodged_from)
            if filter_lodged_to:
                queryset = queryset.filter(due_date__lte=filter_lodged_to)
        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super(ProposalFilterBackend, self).filter_queryset(
            request, queryset, view
        )
        setattr(view, "_datatables_total_count", total_count)
        return queryset


class ProposalRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if "view" in renderer_context and hasattr(
            renderer_context["view"], "_datatables_total_count"
        ):
            data["recordsTotal"] = renderer_context["view"]._datatables_total_count
        return super(ProposalRenderer, self).render(
            data, accepted_media_type, renderer_context
        )


class ProposalPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    queryset = Proposal.objects.none()
    serializer_class = ListProposalSerializer
    page_size = 10

    @property
    def excluded_type(self):
        try:
            return ApplicationType.objects.get(name="E Class")
        except:
            return ApplicationType.objects.none()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Proposal.objects.all()
        elif is_customer(self.request):
            qs = Proposal.objects.filter(
                Q(ind_applicant=user.id)
                | Q(submitter=user.id)
                | Q(proxy_applicant=user.id)
            )

            # TODO: Take into account organisations

            return qs
        return Proposal.objects.none()

    def list(self, request, *args, **kwargs):
        """serializer.data = {ReturnList: 10} [OrderedDict([('id', 4), ('application_type', OrderedDict([('id', 1), ('name_display', 'Registration of Interest'), ('confirmation_text', 'registration of interest'), ('name', 'registration_of_interest'), ('order', 0), ('visible', True), ('application_fee'… View
        User is accessing /external/ page
        """
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        email_user_id_assigned = int(
            request.query_params.get("email_user_id_assigned", "0")
        )

        if email_user_id_assigned:
            qs = qs.filter(
                Q(
                    referrals__in=Referral.objects.filter(
                        referral=email_user_id_assigned
                    )
                )
            )

        qs = qs.distinct()
        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)

    # TODO: check if still required
    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def proposals_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_internal/?format=datatables&draw=1&length=2
        """
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get("org_id")
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def proposals_external(self, request, *args, **kwargs):
        """
        Used by the external dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_external/?format=datatables&draw=1&length=2
        """
        qs = self.get_queryset().exclude(processing_status="discarded")
        # qs = self.filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get("org_id")
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)


class ProposalViewSet(viewsets.ModelViewSet):
    # class ProposalViewSet(VersionableModelViewSetMixin):
    # queryset = Proposal.objects.all()
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer
    lookup_field = "id"

    @property
    def excluded_type(self):
        try:
            return ApplicationType.objects.get(name="E Class")
        except:
            return ApplicationType.objects.none()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):  # user.is_authenticated():
            return Proposal.objects.all()
            # qs = Proposal.objects.all().exclude(application_type=self.excluded_type)
            # return qs.exclude(migrated=True)
            # return Proposal.objects.filter(region__isnull=False)
        elif is_customer(self.request):
            # user_orgs = [org.id for org in user.parkpasses_organisations.all()]
            user_orgs = []  # TODO array of organisations' id for this user
            queryset = Proposal.objects.filter(
                Q(org_applicant_id__in=user_orgs) | Q(submitter=user.id)
            ).exclude(migrated=True)
            # queryset =  Proposal.objects.filter(region__isnull=False).filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            return queryset.exclude(application_type=self.excluded_type)
        logger.warn(
            "User is neither customer nor internal user: {} <{}>".format(
                user.get_full_name(), user.email
            )
        )
        return Proposal.objects.none()

    def get_object(self):

        check_db_connection()
        try:
            obj = super(ProposalViewSet, self).get_object()
        except Exception as e:
            # because current queryset excludes migrated licences
            obj = get_object_or_404(Proposal, id=self.kwargs["id"])
        return obj

    def get_serializer_class(self):
        try:
            return ProposalSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def internal_serializer_class(self):
        try:
            application_type = Proposal.objects.get(
                id=self.kwargs.get("id")
            ).application_type.name
            if application_type == APPLICATION_TYPE_REGISTRATION_OF_INTEREST:
                return InternalProposalSerializer
            elif application_type == APPLICATION_TYPE_LEASE_LICENCE:
                return InternalProposalSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def filter_list(self, request, *args, **kwargs):
        """Used by the internal/external dashboard filters"""
        submitter_qs = (
            self.get_queryset()
            .filter(submitter__isnull=False)
            .distinct("submitter__email")
            .values_list(
                "submitter__first_name", "submitter__last_name", "submitter__email"
            )
        )
        submitters = [
            dict(email=i[2], search_term="{} {} ({})".format(i[0], i[1], i[2]))
            for i in submitter_qs
        ]
        application_types = ApplicationType.objects.filter(visible=True).values_list(
            "name", flat=True
        )
        data = dict(
            submitters=submitters,
            application_types=application_types,
            approval_status_choices=[i[1] for i in Approval.STATUS_CHOICES],
        )
        return Response(data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def compare_list(self, request, *args, **kwargs):
        """Returns the reversion-compare urls --> list"""
        current_revision_id = (
            Version.objects.get_for_object(self.get_object()).first().revision_id
        )
        versions = (
            Version.objects.get_for_object(self.get_object())
            .select_related("revision__user")
            .filter(
                Q(revision__comment__icontains="status")
                | Q(revision_id=current_revision_id)
            )
        )
        version_ids = [i.id for i in versions]
        urls = [
            "?version_id2={}&version_id1={}".format(version_ids[0], version_ids[i + 1])
            for i in range(len(version_ids) - 1)
        ]
        return Response(urls)

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_shapefile_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="shapefile_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_legislative_requirements_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="legislative_requirements_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_risk_factors_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="risk_factors_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_key_milestones_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="key_milestones_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_key_personnel_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="key_personnel_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_staffing_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="staffing_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_market_analysis_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="market_analysis_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_available_activities_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="available_activities_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_financial_capacity_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="financial_capacity_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_capital_investment_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="capital_investment_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_cash_flow_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="cash_flow_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_profit_and_loss_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="profit_and_loss_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_deed_poll_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="deed_poll_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_supporting_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="supporting_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_exclusive_use_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="exclusive_use_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_long_term_use_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="long_term_use_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_consistent_purpose_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="consistent_purpose_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_consistent_plan_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="consistent_plan_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_clearing_vegetation_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="clearing_vegetation_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_ground_disturbing_works_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="ground_disturbing_works_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_heritage_site_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="heritage_site_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_environmentally_sensitive_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="environmentally_sensitive_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_wetlands_impact_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="wetlands_impact_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_building_required_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="building_required_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_significant_change_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="significant_change_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_aboriginal_site_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="aboriginal_site_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_native_title_consultation_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="native_title_consultation_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_mining_tenement_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="mining_tenement_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get("action")
            section = request.POST.get("input_name")
            if action == "list" and "input_name" in request.POST:
                pass

            elif action == "delete" and "document_id" in request.POST:
                document_id = request.POST.get("document_id")
                document = instance.documents.get(id=document_id)

                if (
                    document._file
                    and os.path.isfile(document._file.path)
                    and document.can_delete
                ):
                    os.remove(document._file.path)

                document.delete()
                instance.save(
                    version_comment="Approval File Deleted: {}".format(document.name)
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == "hide" and "document_id" in request.POST:
                document_id = request.POST.get("document_id")
                document = instance.documents.get(id=document_id)

                document.hidden = True
                document.save()
                instance.save(
                    version_comment="File hidden: {}".format(document.name)
                )  # to allow revision to be added to reversion history

            elif (
                action == "save"
                and "input_name" in request.POST
                and "filename" in request.POST
            ):
                proposal_id = request.POST.get("proposal_id")
                filename = request.POST.get("filename")
                _file = request.POST.get("_file")
                if not _file:
                    _file = request.FILES.get("_file")

                document = instance.documents.get_or_create(
                    input_name=section, name=filename
                )[0]
                path = default_storage.save(
                    "{}/proposals/{}/documents/{}".format(
                        settings.MEDIA_APP_DIR, proposal_id, filename
                    ),
                    ContentFile(_file.read()),
                )

                document._file = path
                document.save()
                instance.save(
                    version_comment="File Added: {}".format(filename)
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return Response(
                [
                    dict(
                        input_name=d.input_name,
                        name=d.name,
                        file=d._file.url,
                        id=d.id,
                        can_delete=d.can_delete,
                        can_hide=d.can_hide,
                    )
                    for d in instance.documents.filter(input_name=section, hidden=False)
                    if d._file
                ]
            )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_onhold_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get("action")
            section = request.POST.get("input_name")
            if action == "list" and "input_name" in request.POST:
                pass

            #            elif action == 'delete' and 'document_id' in request.POST:
            #                document_id = request.POST.get('document_id')
            #                document = instance.onhold_documents.get(id=document_id)
            #
            #                if document._file and os.path.isfile(document._file.path) and document.can_delete:
            #                    os.remove(document._file.path)
            #
            #                document.delete()
            #                instance.save(version_comment='OnHold File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history
            #                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == "delete" and "document_id" in request.POST:
                document_id = request.POST.get("document_id")
                document = instance.onhold_documents.get(id=document_id)

                document.visible = False
                document.save()
                instance.save(
                    version_comment="OnHold File Hidden: {}".format(document.name)
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif (
                action == "save"
                and "input_name" in request.POST
                and "filename" in request.POST
            ):
                proposal_id = request.POST.get("proposal_id")
                filename = request.POST.get("filename")
                _file = request.POST.get("_file")
                if not _file:
                    _file = request.FILES.get("_file")

                document = instance.onhold_documents.get_or_create(
                    input_name=section, name=filename
                )[0]
                path = default_storage.save(
                    "{}/proposals/{}/onhold/{}".format(
                        settings.MEDIA_APP_DIR, proposal_id, filename
                    ),
                    ContentFile(_file.read()),
                )

                document._file = path
                document.save()
                instance.save(
                    version_comment="On Hold File Added: {}".format(filename)
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return Response(
                [
                    dict(
                        input_name=d.input_name,
                        name=d.name,
                        file=d._file.url,
                        id=d.id,
                        can_delete=d.can_delete,
                    )
                    for d in instance.onhold_documents.filter(
                        input_name=section, visible=True
                    )
                    if d._file
                ]
            )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_qaofficer_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get("action")
            section = request.POST.get("input_name")
            if action == "list" and "input_name" in request.POST:
                pass

            elif action == "delete" and "document_id" in request.POST:
                document_id = request.POST.get("document_id")
                document = instance.qaofficer_documents.get(id=document_id)

                document.visible = False
                document.save()
                instance.save(
                    version_comment="QA Officer File Hidden: {}".format(document.name)
                )  # to allow revision to be added to reversion history

            elif (
                action == "save"
                and "input_name" in request.POST
                and "filename" in request.POST
            ):
                proposal_id = request.POST.get("proposal_id")
                filename = request.POST.get("filename")
                _file = request.POST.get("_file")
                if not _file:
                    _file = request.FILES.get("_file")

                document = instance.qaofficer_documents.get_or_create(
                    input_name=section, name=filename
                )[0]
                path = default_storage.save(
                    "{}/proposals/{}/qaofficer/{}".format(
                        settings.MEDIA_APP_DIR, proposal_id, filename
                    ),
                    ContentFile(_file.read()),
                )

                document._file = path
                document.save()
                instance.save(
                    version_comment="QA Officer File Added: {}".format(filename)
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return Response(
                [
                    dict(
                        input_name=d.input_name,
                        name=d.name,
                        file=d._file.url,
                        id=d.id,
                        can_delete=d.can_delete,
                    )
                    for d in instance.qaofficer_documents.filter(
                        input_name=section, visible=True
                    )
                    if d._file
                ]
            )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def list(self, request, *args, **kwargs):
        proposals = self.get_queryset()

        statuses = list(map(lambda x: x[0], Proposal.PROCESSING_STATUS_CHOICES))
        types = list(map(lambda x: x[0], APPLICATION_TYPES))
        type = request.query_params.get("type", "")
        status = request.query_params.get("status", "")
        if status in statuses and type in types:
            # both status and type exists
            proposals = proposals.filter(
                Q(processing_status=status) & Q(application_type__name=type)
            )
        serializer = ListProposalMinimalSerializer(
            proposals, context={"request": request}, many=True
        )
        return Response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def list_paginated(self, request, *args, **kwargs):
        """
        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset()
        paginator = PageNumberPagination()
        # paginator = LimitOffsetPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(
            result_page, context={"request": request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ProposalUserActionSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ProposalLogEntrySerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                mutable = request.data._mutable
                request.data._mutable = True
                request.data["proposal"] = "{}".format(instance.id)
                request.data["staff"] = "{}".format(request.user.id)
                request.data._mutable = mutable
                serializer = ProposalLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def requirements(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # qs = instance.requirements.all()
            qs = instance.requirements.all().exclude(is_deleted=True)
            # qs=qs.order_by('order')
            serializer = ProposalRequirementSerializer(
                qs, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.amendment_requests
            qs = qs.filter(status="requested")
            serializer = AmendmentRequestDisplaySerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().exclude(processing_status="discarded")
        serializer = ListProposalSerializer(qs, context={"request": request}, many=True)
        return Response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def user_list_paginated(self, request, *args, **kwargs):
        """
        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
        otherwise all serializers will use the default pagination class

        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset().exclude(processing_status="discarded")
        paginator = DatatablesPageNumberPagination()
        paginator.page_size = proposals.count()
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(
            result_page, context={"request": request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def list_paginated(self, request, *args, **kwargs):
        """
        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
        otherwise all serializers will use the default pagination class

        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset()
        paginator = DatatablesPageNumberPagination()
        paginator.page_size = proposals.count()
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(
            result_page, context={"request": request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)

    # Documents on Activities(land)and Activities(Marine) tab for T-Class related to required document questions
    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_required_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get("action")
            section = request.POST.get("input_name")
            required_doc_id = request.POST.get("required_doc_id")
            if action == "list" and "required_doc_id" in request.POST:
                pass

            elif action == "delete" and "document_id" in request.POST:
                document_id = request.POST.get("document_id")
                document = instance.required_documents.get(id=document_id)

                if (
                    document._file
                    and os.path.isfile(document._file.path)
                    and document.can_delete
                ):
                    os.remove(document._file.path)

                document.delete()
                instance.save(
                    version_comment="Required document File Deleted: {}".format(
                        document.name
                    )
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == "hide" and "document_id" in request.POST:
                document_id = request.POST.get("document_id")
                document = instance.required_documents.get(id=document_id)

                document.hidden = True
                document.save()
                instance.save(
                    version_comment="File hidden: {}".format(document.name)
                )  # to allow revision to be added to reversion history

            elif (
                action == "save"
                and "input_name"
                and "required_doc_id" in request.POST
                and "filename" in request.POST
            ):
                proposal_id = request.POST.get("proposal_id")
                filename = request.POST.get("filename")
                _file = request.POST.get("_file")
                if not _file:
                    _file = request.FILES.get("_file")

                required_doc_instance = RequiredDocument.objects.get(id=required_doc_id)
                document = instance.required_documents.get_or_create(
                    input_name=section,
                    name=filename,
                    required_doc=required_doc_instance,
                )[0]
                path = default_storage.save(
                    "{}/proposals/{}/required_documents/{}".format(
                        settings.MEDIA_APP_DIR, proposal_id, filename
                    ),
                    ContentFile(_file.read()),
                )

                document._file = path
                document.save()
                instance.save(
                    version_comment="File Added: {}".format(filename)
                )  # to allow revision to be added to reversion history
                # instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return Response(
                [
                    dict(
                        input_name=d.input_name,
                        name=d.name,
                        file=d._file.url,
                        id=d.id,
                        can_delete=d.can_delete,
                        can_hide=d.can_hide,
                    )
                    for d in instance.required_documents.filter(
                        required_doc=required_doc_id, hidden=False
                    )
                    if d._file
                ]
            )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def internal_proposal(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalProposalSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(methods=["post"], detail=True)
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            save_proponent_data(instance, request, self)
            # return redirect(reverse('external'))
            proposal_submit(instance, request)
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=["post"], detail=True)
    @renderer_classes((JSONRenderer,))
    def validate_map_files(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.validate_map_files(request)
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
            # return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_officer(request, request.user)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get("assessor_id", None)
            user = None
            if not user_id:
                raise serializers.ValidationError("An assessor id is required")
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError(
                    "A user with the id passed in does not exist"
                )
            instance.assign_officer(request, user)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def switch_status(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get("status")
            approver_comment = request.data.get("approver_comment")
            if not status:
                raise serializers.ValidationError("Status is required")
            else:
                if not status in [
                    "with_assessor",
                    "with_assessor_conditions",
                    "with_approver",
                ]:
                    raise serializers.ValidationError(
                        "The status provided is not allowed"
                    )
            instance.move_to_status(request, status, approver_comment)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            # if instance.application_type.name==ApplicationType.TCLASS:
            #     serializer = InternalProposalSerializer(instance,context={'request':request})
            # elif instance.application_type.name==ApplicationType.FILMING:
            #     serializer = InternalFilmingProposalSerializer(instance,context={'request':request})
            # elif instance.application_type.name==ApplicationType.EVENT:
            #     serializer = InternalProposalSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def reissue_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get("status")
            if not status:
                raise serializers.ValidationError("Status is required")
            else:
                # if instance.application_type.name==ApplicationType.FILMING and instance.filming_approval_type=='lawful_authority':
                #   status='with_assessor'
                # else:
                if not status in ["with_approver"]:
                    raise serializers.ValidationError(
                        "The status provided is not allowed"
                    )
            instance.reissue_approval(request, status)
            serializer = InternalProposalSerializer(
                instance, context={"request": request}
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def renew_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.renew_approval(request)
            serializer = SaveProposalSerializer(instance, context={"request": request})
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            if hasattr(e, "message"):
                raise serializers.ValidationError(e.message)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def amend_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.amend_approval(request)
            serializer = SaveProposalSerializer(instance, context={"request": request})
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            if hasattr(e, "message"):
                raise serializers.ValidationError(e.message)

    @basic_exception_handler
    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def proposed_approval(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProposedApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.proposed_approval(request, serializer.validated_data)
        # serializer = InternalProposalSerializer(instance,context={'request':request})
        serializer_class = self.internal_serializer_class()
        serializer = serializer_class(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def approval_level_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.assing_approval_level_document(request)
            serializer = InternalProposalSerializer(
                instance, context={"request": request}
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def final_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_approval(request, serializer.validated_data)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def proposed_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PropedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_decline(request, serializer.validated_data)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def final_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PropedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_decline(request, serializer.validated_data)
            # serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def on_hold(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                is_onhold = eval(request.data.get("onhold"))
                data = {}
                if is_onhold:
                    data["type"] = "onhold"
                    instance.on_hold(request)
                else:
                    data["type"] = "onhold_remove"
                    instance.on_hold_remove(request)

                data["proposal"] = "{}".format(instance.id)
                data["staff"] = "{}".format(request.user.id)
                data["text"] = request.user.get_full_name() + ": {}".format(
                    request.data["text"]
                )
                data["subject"] = request.user.get_full_name() + ": {}".format(
                    request.data["text"]
                )
                serializer = ProposalLogEntrySerializer(data=data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()

                # save the files
                documents_qs = instance.onhold_documents.filter(
                    input_name="on_hold_file", visible=True
                )
                for f in documents_qs:
                    document = comms.documents.create(_file=f._file, name=f.name)
                    # document = comms.documents.create()
                    # document.name = f.name
                    # document._file = f._file #.strip('/media')
                    document.input_name = f.input_name
                    document.can_delete = True
                    document.save()
                # end save documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def with_qaofficer(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                is_with_qaofficer = eval(request.data.get("with_qaofficer"))
                data = {}
                if is_with_qaofficer:
                    data["type"] = "with_qaofficer"
                    instance.with_qaofficer(request)
                else:
                    data["type"] = "with_qaofficer_completed"
                    instance.with_qaofficer_completed(request)

                data["proposal"] = "{}".format(instance.id)
                data["staff"] = "{}".format(request.user.id)
                data["text"] = request.user.get_full_name() + ": {}".format(
                    request.data["text"]
                )
                data["subject"] = request.user.get_full_name() + ": {}".format(
                    request.data["text"]
                )
                serializer = ProposalLogEntrySerializer(data=data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()

                # Save the files
                document_qs = []
                if is_with_qaofficer:
                    # Get the list of documents attached by assessor when sending application to QA officer
                    documents_qs = instance.qaofficer_documents.filter(
                        input_name="assessor_qa_file", visible=True
                    )
                else:
                    # Get the list of documents attached by QA officer when sending application back to assessor
                    documents_qs = instance.qaofficer_documents.filter(
                        input_name="qaofficer_file", visible=True
                    )
                for f in documents_qs:
                    document = comms.documents.create(_file=f._file, name=f.name)
                    # document = comms.documents.create()
                    # document.name = f.name
                    # document._file = f._file #.strip('/media')
                    document.input_name = f.input_name
                    document.can_delete = True
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=["post"], detail=True)
    @renderer_classes((JSONRenderer,))
    def draft(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            save_proponent_data(instance, request, self)
            # return redirect(reverse('external'))
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

    @detail_route(methods=["post"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def complete_referral(self, request, *args, **kwargs):
        instance = self.get_object()
        save_referral_data(instance, request, True)

        # TODO: complete referral here

        return Response({})

    @detail_route(methods=["post"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def referral_save(self, request, *args, **kwargs):
        instance = self.get_object()
        save_referral_data(instance, request, False)
        return Response({})

    @detail_route(methods=["post"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def assessor_save(self, request, *args, **kwargs):
        instance = self.get_object()
        save_assessor_data(instance, request, self)
        return redirect(reverse("external"))

    @detail_route(methods=["post"], detail=True)
    @basic_exception_handler
    def assesor_send_referral(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SendReferralSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        # text=serializer.validated_data['text']
        # instance.send_referral(request,serializer.validated_data['email'])
        instance.send_referral(
            request,
            serializer.validated_data["email"],
            serializer.validated_data["text"],
        )
        # serializer = InternalProposalSerializer(instance,context={'request':request})
        serializer_class = self.internal_serializer_class()
        serializer = serializer_class(instance, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                print("request.data")
                print(request.data)
                http_status = status.HTTP_200_OK
                application_type_str = request.data.get("application_type", {}).get(
                    "code"
                )

                application_type = ApplicationType.objects.get(
                    name=application_type_str
                )
                proposal_type = ProposalType.objects.get(code="new")

                data = {
                    "org_applicant": request.data.get("org_applicant"),
                    "ind_applicant": request.user.id
                    if not request.data.get("org_applicant")
                    else None,  # if no org_applicant, assume this application is for individual.
                    "application_type_id": application_type.id,
                    "proposal_type_id": proposal_type.id,
                }
                print(data)
                print("before serializer")
                serializer = CreateProposalSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                # serializer.save()
                instance = serializer.save()

                serializer = SaveProposalSerializer(instance)
                return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            if application_name == ApplicationType.TCLASS:
                serializer = SaveProposalSerializer(instance, data=request.data)
            elif application_name == ApplicationType.FILMING:
                serializer = ProposalFilmingOtherDetailsSerializer(
                    data=other_details_data
                )
            elif application_name == ApplicationType.EVENT:
                serializer = ProposalEventOtherDetailsSerializer(
                    data=other_details_data
                )

            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            serializer = SaveProposalSerializer(
                instance,
                {"processing_status": "discarded", "previous_application": None},
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=http_status)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
