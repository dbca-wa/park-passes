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
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Count, F, Sum
from django.utils import timezone
from docxtpl import DocxTemplate

from parkpasses.components.orders.models import Order, OrderItem
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
                no_payment_orders = Order.objects.filter(
                    retailer_group=retailer_group,
                    is_no_payment=True,
                )
            else:
                no_payment_orders = Order.objects.filter(
                    retailer_group=retailer_group,
                    is_no_payment=True,
                    datetime_created__gte=first_day_of_previous_month,
                    datetime_created__lte=last_day_of_previous_month,
                )
            no_payment_order_count = len(no_payment_orders)
            self.stdout.write(
                f"\t -- Found {no_payment_order_count} No Payment Orders.\n\n"
            )

            if 0 == no_payment_order_count:
                continue

            total = Decimal(0.00)
            for order in no_payment_orders:
                total += order.total

            commission_amount = Decimal(
                total * (retailer_group.commission_percentage / 100)
            ).quantize(Decimal("0.01"))

            total_payable = Decimal(total - commission_amount).quantize(Decimal("0.01"))

            context = {
                "organisation": organisation,
                "retailer_group": retailer_group,
                "orders": no_payment_orders,
                "date": today,
                "commission_percentage": f"{retailer_group.commission_percentage}%",
                "commission_amount": f"${commission_amount}",
                "total_sales": f"${total}",
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

            content_type = ContentType.objects.get_for_model(Pass)
            pass_id_strings = OrderItem.objects.filter(
                order__in=no_payment_orders, content_type=content_type
            ).values_list("object_id", flat=True)
            pass_ids = [int(i) for i in pass_id_strings]

            total_sales_by_pass_type = (
                Pass.objects.filter(id__in=pass_ids)
                .values("option__pricing_window__pass_type__display_name")
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
                "total_sales": f"${total}",
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
