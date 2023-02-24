import logging

import requests
from django.conf import settings
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from ledger_api_client.utils import generate_payment_session
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
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
        due_date = timezone.now() - timezone.timedelta(
            days=settings.RETAILER_INVOICE_DUE_DAYS
        )
        if 0 < len(user_retailer_groups):
            return Report.objects.annotate(
                overdue=ExpressionWrapper(
                    Q(datetime_created__lte=due_date, processing_status=Report.UNPAID),
                    output_field=BooleanField(),
                )
            ).filter(retailer_group__in=user_retailer_groups)
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

    @action(methods=["GET"], detail=True, url_path="retrieve-statement-pdf")
    def retrieve_statement_pdf(self, request, *args, **kwargs):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id", flat=True)
            report = self.get_object()
            if report.retailer_group.id in list(retailer_groups):
                if report.statement:
                    return FileResponse(report.statement)
        raise Http404

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice-receipt")
    def retrieve_invoice_receipt(self, request, *args, **kwargs):
        report = self.get_object()
        invoice_url = report.invoice_link
        if invoice_url:
            response = requests.get(invoice_url)
            return FileResponse(response, content_type="application/pdf")

        raise Http404

    @action(methods=["GET"], detail=True, url_path="pay-invoice")
    def pay_invoice(self, request, *args, **kwargs):
        logger.info("Pay Invoice")
        report = self.get_object()
        return_url = reverse(
            "retailer-reports-pay-invoice-success",
            kwargs={"report_number": report.report_number},
        )
        fallback_url = reverse(
            "retailer-reports-pay-invoice-failure",
            kwargs={"report_number": report.report_number},
        )

        logger.info(f"Return URL: {return_url}")
        logger.info(f"Fallback URL: {fallback_url}")
        payment_session = generate_payment_session(
            request,
            report.invoice_reference,
            request.build_absolute_uri(return_url),
            request.build_absolute_uri(fallback_url),
        )
        logger.info(f"Payment session: {payment_session}")

        if 200 == payment_session["status"]:
            return redirect(reverse("ledgergw-payment-details"))

        return redirect(fallback_url)


class PayInvoiceSuccessCallbackView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, uuid, format=None):
        logger.info("Park passes Pay Invoice Success View get method called.")

        if (
            uuid
            and Report.objects.filter(
                uuid=uuid, processing_status=Report.UNPAID
            ).exists()
        ):
            logger.info(
                f"Invoice uuid: {uuid}.",
            )
            report = Report.objects.get(uuid=uuid)
            report.processing_status = Report.PAID
            report.save()

            logger.info(
                "Returning status.HTTP_200_OK. Report marked as paid successfully.",
            )
            # this end-point is called by an unmonitored get request in ledger so there is no point having a
            # a response body however we will return a status in case this is used on the ledger end in future
            return Response(status=status.HTTP_200_OK)

        # If there is no uuid to identify the cart then send a bad request status back in case ledger can
        # do something with this in future
        logger.info(
            "Returning status.HTTP_400_BAD_REQUEST bad request as there "
            f"was not an unpaid report invoice with uuid: {uuid}."
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
    due_date = timezone.now() - timezone.timedelta(
        days=settings.RETAILER_INVOICE_DUE_DAYS
    )
    queryset = Report.objects.annotate(
        overdue=ExpressionWrapper(
            Q(datetime_created__lte=due_date, processing_status=Report.UNPAID),
            output_field=BooleanField(),
        )
    ).exclude(
        retailer_group__ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
    )
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

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice-receipt")
    def retrieve_invoice_receipt(self, request, *args, **kwargs):
        report = self.get_object()
        invoice_url = report.invoice_link
        if invoice_url:
            response = requests.get(invoice_url)
            return FileResponse(response, content_type="application/pdf")

        raise Http404

    @action(methods=["GET"], detail=True, url_path="retrieve-statement-pdf")
    def retrieve_statement_pdf(self, request, *args, **kwargs):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id", flat=True)
            report = self.get_object()
            if report.retailer_group.id in list(retailer_groups):
                if report.statement:
                    return FileResponse(report.statement)
        raise Http404
