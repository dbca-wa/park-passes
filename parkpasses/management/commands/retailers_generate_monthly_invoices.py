"""
This management commands generates reports and invoices for each retailer for the previous month

Usage: ./manage.sh retailers_generate_monthly_invoices
        (this command should be run on the 1st day of every month by a cron job or task runner not manually)

"""
import logging
import os
import subprocess
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, F, Sum
from django.utils import timezone
from docxtpl import DocxTemplate

from parkpasses.components.passes.models import Pass
from parkpasses.components.reports.models import Report
from parkpasses.components.retailers.models import RetailerGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generates invoices for each retailer for the previous month"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Add the test flag will output what emails would be sent without actually sending them.",
        )

    def handle(self, *args, **options):
        organisation = settings.ORGANISATION
        invoice_template_docx = DocxTemplate(
            "parkpasses/management/templates/RetailerGroupInvoiceTemplate.docx"
        )
        report_template_docx = DocxTemplate(
            "parkpasses/management/templates/RetailerGroupReportTemplate.docx"
        )

        today = timezone.make_aware(
            datetime.combine(timezone.now(), datetime.min.time())
        )
        first_day_of_this_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_this_month - timezone.timedelta(
            days=1
        )
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        if options["test"]:
            first_day_of_previous_month = first_day_of_this_month
            last_day_of_previous_month = first_day_of_this_month + relativedelta(day=31)

        self.stdout.write(
            f"\nGenerating Reports for date range: {first_day_of_previous_month} to {last_day_of_previous_month}\n\n"
        )

        retailer_groups = RetailerGroup.objects.all()

        for retailer_group in retailer_groups:
            self.stdout.write(f"\tGenerating Invoice for {retailer_group}")
            if options["test"]:
                # To make sure we have records when testing just select all no_payment_orders
                # regardless of the date
                passes = Pass.objects.exclude(cancellation__isnull=True).filter(
                    sold_via=retailer_group,
                )
                cancellations = Pass.objects.filter(
                    cancellation__isnull=True,
                    sold_via=retailer_group,
                    cancellation__null=True,
                )
            else:
                passes = Pass.objects.filter(
                    cancellation__isnull=True,
                    sold_via=retailer_group,
                    datetime_created__gte=first_day_of_previous_month,
                    datetime_created__lte=last_day_of_previous_month,
                )
                cancellations = Pass.objects.filter(
                    sold_via=retailer_group,
                    cancellation__isnull=False,
                    cancellation__datetime_cancelled__gte=first_day_of_previous_month,
                    cancellation__datetime_cancelled__lte=last_day_of_previous_month,
                ).order_by("cancellation__datetime_cancelled")

            pass_count = len(passes)
            cancellation_count = len(cancellations)
            self.stdout.write(
                f"\t -- Found {pass_count} Passes and {cancellation_count} cancellations.\n\n"
            )

            if 0 == pass_count:
                continue

            total_sales = Decimal(0.00)
            for park_pass in passes:
                total_sales += park_pass.price

            total_refunds = Decimal(0.00)
            for park_pass in cancellations:
                total_refunds += park_pass.pro_rata_refund_amount

            grand_total = total_sales - total_refunds

            commission_amount = Decimal(
                grand_total * (retailer_group.commission_percentage / 100)
            ).quantize(Decimal("0.01"))

            total_payable = Decimal(grand_total - commission_amount).quantize(
                Decimal("0.01")
            )

            context = {
                "organisation": organisation,
                "retailer_group": retailer_group,
                "passes": passes,
                "cancellations": cancellations,
                "date": today,
                "commission_percentage": f"{retailer_group.commission_percentage}%",
                "commission_amount": f"${commission_amount}",
                "total_sales": f"${total_sales}",
                "total_refunds": f"${total_refunds}",
                "grand_total": f"${grand_total}",
                "total_payable": f"${total_payable}",
            }
            invoice_template_docx.render(context)
            invoice_filename = f"Park Passes Invoice - {retailer_group.name} - {first_day_of_previous_month.date()} "
            invoice_filename += f"{last_day_of_previous_month.date()}.docx"
            invoice_path = f"{settings.RETAILER_GROUP_INVOICE_ROOT}/{retailer_group.id}/{invoice_filename}"
            Path(f"{settings.RETAILER_GROUP_INVOICE_ROOT}/{retailer_group.id}").mkdir(
                parents=True, exist_ok=True
            )
            invoice_template_docx.save(invoice_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--convert-to",
                    "pdf",
                    invoice_path,
                    "--outdir",
                    f"{settings.RETAILER_GROUP_INVOICE_ROOT}/{retailer_group.id}",
                ]
            )

            total_sales_by_pass_type = (
                passes.values("option__pricing_window__pass_type__display_name")
                .order_by("option__pricing_window__pass_type__display_name")
                .annotate(total_sales=Sum("option__price"))
                .annotate(
                    pass_type=F("option__pricing_window__pass_type__display_name")
                )
                .annotate(pass_count=Count("id"))
            )

            context = {
                "organisation": organisation,
                "rg": retailer_group,
                "total_sales_by_pass_type": total_sales_by_pass_type,
                "date": today,
                "commission_percentage": f"{retailer_group.commission_percentage}%",
                "commission_amount": f"${commission_amount}",
                "total_sales": f"${total_sales}",
                "total_refunds": f"${total_refunds}",
                "grand_total": f"${grand_total}",
                "total_payable": f"${total_payable}",
            }
            report_template_docx.render(context)
            report_filename = f"Park Passes Report - {retailer_group.name} - {first_day_of_previous_month.date()} "
            report_filename += f"{last_day_of_previous_month.date()}.docx"
            report_path = f"{settings.RETAILER_GROUP_REPORT_ROOT}/{retailer_group.id}/{report_filename}"
            Path(f"{settings.RETAILER_GROUP_REPORT_ROOT}/{retailer_group.id}").mkdir(
                parents=True, exist_ok=True
            )
            report_template_docx.save(report_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--convert-to",
                    "pdf",
                    report_path,
                    "--outdir",
                    f"{settings.RETAILER_GROUP_REPORT_ROOT}/{retailer_group.id}",
                ]
            )

            # If regenerating reports don't create a new report record for the same month and year
            if Report.objects.filter(
                retailer_group=retailer_group,
                datetime_created__year=first_day_of_previous_month.year,
                datetime_created__month=first_day_of_previous_month.month,
            ).exists():
                report = Report.objects.get(
                    retailer_group=retailer_group,
                    datetime_created__year=first_day_of_previous_month.year,
                    datetime_created__month=first_day_of_previous_month.month,
                )
            else:
                report = Report.objects.create(retailer_group=retailer_group)
            report.report.name = report_path.replace("docx", "pdf")
            report.invoice.name = invoice_path.replace("docx", "pdf")
            report.save()

            os.remove(report_path)
            os.remove(invoice_path)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\tGenerated Report: {os.path.basename(report.invoice.name)}\n"
                )
            )
