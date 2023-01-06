import calendar
import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from ledger_api_client.utils import create_basket_session, create_checkout_session
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.main.api import (
    CustomDatatablesListMixin,
    CustomDatatablesRenderer,
)
from parkpasses.components.passes.models import Pass
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

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice-receipt")
    def retrieve_invoice_receipt(self, request, *args, **kwargs):
        report = self.get_object()
        invoice_url = report.invoice_link
        if invoice_url:
            response = requests.get(invoice_url)
            return FileResponse(response, content_type="application/pdf")

        raise Http404

    @action(methods=["POST"], detail=True, url_path="pay-invoice")
    def pay_invoice(self, request, *args, **kwargs):
        logger.info("Pay Invoice")
        report = self.get_object()
        retailer_group = report.retailer_group

        date_invoice_generated = report.datetime_created.date()
        first_day_of_this_month = date_invoice_generated.replace(day=1)
        last_day_of_previous_month = first_day_of_this_month - timezone.timedelta(
            days=1
        )
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
        month_year = first_day_of_previous_month.strftime("%B %Y")
        ledger_description = f"Park Passes Sales for the Month of { month_year }"

        logger.info("Retrieving " + ledger_description)

        passes = Pass.objects.filter(
            sold_via=retailer_group,
            datetime_created__range=(
                first_day_of_previous_month,
                last_day_of_previous_month,
            ),
        )

        if 0 == passes.count() and settings.DEBUG:
            logger.info(
                "No passes found in the month before the invoice was generated."
                + "Trying to find passes in the same month the invoice was generated."
            )
            # If the genereate monthly invoices management command was run with the --test flag
            # then we need to select the passes sold in the same month the report was generated
            last_day_of_this_month_number = calendar.monthrange(
                date_invoice_generated.year, date_invoice_generated.month
            )[1]
            last_day_of_this_month = date_invoice_generated.replace(
                day=last_day_of_this_month_number
            )
            passes = Pass.objects.filter(
                sold_via=retailer_group,
                datetime_created__range=(
                    first_day_of_this_month,
                    last_day_of_this_month,
                ),
            )
        logger.info(f"Found {len(passes)} passes.")

        invoice_amount = Decimal(0.00)
        for park_pass in passes:
            invoice_amount += park_pass.price_after_concession_applied

        if invoice_amount <= Decimal(0.00):
            return redirect(reverse("retailer-reports"))

        commission_amount = (
            Decimal(invoice_amount / 100).quantize(Decimal("0.01"))
            * retailer_group.commission_percentage
        )
        commission_ledger_description = (
            f"Park Passes Sales for the Month of { month_year }"
        )

        if settings.DEBUG:
            invoice_amount = int(invoice_amount)
            commission_amount = int(commission_amount)
            ledger_description += " (Price rounded for dev env)"
            commission_ledger_description += " (Price rounded for dev env)"

        ledger_order_lines = [
            {
                "ledger_description": ledger_description,
                "quantity": 1,
                "price_incl_tax": str(invoice_amount),
                "oracle_code": retailer_group.oracle_code,
                "line_status": settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS,
            },
            {
                "ledger_description": commission_ledger_description,
                "quantity": 1,
                "price_incl_tax": str(-abs(commission_amount)),
                "oracle_code": retailer_group.oracle_code,
                "line_status": settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS,
            },
        ]
        booking_reference = report.uuid
        basket_parameters = CartUtils.get_basket_parameters(
            ledger_order_lines,
            booking_reference,
            is_no_payment=False,
        )
        create_basket_session(request, request.user.id, basket_parameters)

        invoice_text = f"Unique Identifier: {booking_reference}"
        return_url = request.build_absolute_uri(
            reverse(
                "retailer-reports-pay-invoice-success",
                kwargs={
                    "report_number": report.report_number,
                },
            )
        )
        return_preload_url = request.build_absolute_uri(
            reverse(
                "ledger-api-retailer-invoice-success-callback",
                kwargs={
                    "uuid": booking_reference,
                },
            )
        )
        checkout_parameters = CartUtils.get_checkout_parameters(
            request, return_url, return_preload_url, request.user.id, invoice_text
        )
        logger.info("Checkout_parameters = " + str(checkout_parameters))

        create_checkout_session(request, checkout_parameters)

        return redirect(reverse("ledgergw-payment-details"))


class PayInvoiceSuccessCallbackView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, uuid, format=None):
        logger.info("Park passes Pay Invoice Success View get method called.")
        invoice_reference = request.GET.get("invoice", "false")

        if uuid and invoice_reference and Report.objects.filter(uuid=uuid).exists():
            logger.info(
                f"Invoice reference: {invoice_reference} and uuid: {uuid}.",
            )
            report = Report.objects.get(uuid=uuid)
            report.invoice_reference = invoice_reference
            report.processing_status = Report.PAID
            report.save()

            logger.info(
                "Returning status.HTTP_204_NO_CONTENT. Report marked as paid successfully.",
            )
            # this end-point is called by an unmonitored get request in ledger so there is no point having a
            # a response body however we will return a status in case this is used on the ledger end in future
            return Response(status=status.HTTP_204_NO_CONTENT)

        # If there is no uuid to identify the cart then send a bad request status back in case ledger can
        # do something with this in future
        logger.info(
            "Returning status.HTTP_400_BAD_REQUEST bad request as there was not a uuid and invoice_reference."
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
    queryset = Report.objects.exclude(
        retailer_group__name=settings.PARKPASSES_DEFAULT_SOLD_VIA
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
