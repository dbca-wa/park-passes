import logging

from django.http import FileResponse, Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.main.api import (
    CustomDatatablesListMixin,
    CustomDatatablesRenderer,
)
from parkpasses.components.reports.models import Report
from parkpasses.components.reports.serializers import (
    InternalReportSerializer,
    RetailerReportSerializer,
)
from parkpasses.components.retailers.models import RetailerGroupUser
from parkpasses.helpers import get_retailer_group_ids_for_user
from parkpasses.permissions import IsInternal, IsRetailer

logger = logging.getLogger(__name__)


class RetailerReportFilterBackend(DatatablesFilterBackend):
    """
    Custom Filters for Internal Report Viewset
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        processing_status = request.GET.get("processing_status")
        datetime_created_from = request.GET.get("datetime_created_from")
        datetime_created_to = request.GET.get("datetime_created_to")

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

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


class RetailerReportViewSet(CustomDatatablesListMixin, viewsets.ModelViewSet):
    """
    A ViewSet for retailers to perform actions on reports.
    """

    model = Report
    permission_classes = [IsRetailer]
    serializer_class = RetailerReportSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (RetailerReportFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    def get_queryset(self):
        user_retailer_groups = get_retailer_group_ids_for_user(self.request)
        if 0 < len(user_retailer_groups):
            return Report.objects.filter(retailer_group__in=user_retailer_groups)
        return Report.objects.none()

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice-pdf")
    def retrieve_invoice_pdf(self, request, *args, **kwargs):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id", flat=True)
            report = self.get_object()
            if report.retailer_group.id in list(retailer_groups):
                if report.invoice:
                    return FileResponse(report.invoice)
        raise Http404

    @action(methods=["GET"], detail=True, url_path="retrieve-report-pdf")
    def retrieve_report_pdf(self, request, *args, **kwargs):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id", flat=True)
            report = self.get_object()
            if report.retailer_group.id in list(retailer_groups):
                if report.report:
                    return FileResponse(report.report)
        raise Http404


class ReportFilterBackend(DatatablesFilterBackend):
    """
    Custom Filters for Internal Report Viewset
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        retailer_group = request.GET.get("retailer_group")
        processing_status = request.GET.get("processing_status")
        datetime_created_from = request.GET.get("datetime_created_from")
        datetime_created_to = request.GET.get("datetime_created_to")

        if retailer_group:
            queryset = queryset.filter(retailer_group_id=retailer_group)

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

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


class InternalReportViewSet(CustomDatatablesListMixin, viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on reports.
    """

    model = Report
    queryset = Report.objects.all()
    permission_classes = [IsInternal]
    serializer_class = InternalReportSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (ReportFilterBackend,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, CustomDatatablesRenderer)

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice-pdf")
    def retrieve_invoice_pdf(self, request, *args, **kwargs):
        report = self.get_object()
        if report.invoice:
            return FileResponse(report.invoice)
        raise Http404

    @action(methods=["GET"], detail=True, url_path="retrieve-report-pdf")
    def retrieve_report_pdf(self, request, *args, **kwargs):
        report = self.get_object()
        if report.report:
            return FileResponse(report.report)
        raise Http404
