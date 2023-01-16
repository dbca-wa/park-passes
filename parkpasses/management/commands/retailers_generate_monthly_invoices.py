"""
This management commands generates reports and invoices for each retailer for the previous month

Usage: ./manage.sh retailers_generate_monthly_invoices
        (this command should be run on the 1st day of every month by a cron job or task runner not manually)

"""
import logging
import os
import subprocess
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
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

        retailer_groups = RetailerGroup.objects.exclude(
            ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
        )

        for retailer_group in retailer_groups:
            admin_users = retailer_group.retailer_group_users.filter(is_admin=True)
            if 0 == admin_users.count():
                logger.critical(
                    f"Unable to generate monthly invoice for retailer group: {retailer_group}"
                    " as there is are no admin users for this retailer group."
                )
                continue
            user_to_add_to_invoice = admin_users.first()
            logger.info(user_to_add_to_invoice)  # TODO: remove this line
            self.stdout.write(f"\tGenerating Invoice for {retailer_group}")
            passes = Pass.objects.filter(
                sold_via=retailer_group,
                datetime_created__range=(
                    first_day_of_previous_month,
                    last_day_of_previous_month,
                ),
            ).order_by("datetime_created")

            pass_count = len(passes)
            self.stdout.write(f"\t -- Found {pass_count} Passes.\n\n")

            if 0 == pass_count:
                continue

            invoice_uuid = uuid.uuid4()

            total_sales = Decimal(0.00)
            for park_pass in passes:
                total_sales += park_pass.price_after_concession_applied.quantize(
                    Decimal("0.01")
                )

            total_sales = total_sales.quantize(Decimal("0.01"))

            commission_amount = Decimal(
                total_sales * (retailer_group.commission_percentage / 100)
            ).quantize(Decimal("0.01"))

            total_payable = Decimal(total_sales - commission_amount).quantize(
                Decimal("0.01")
            )

            context = {
                "invoice_uuid": invoice_uuid,
                "organisation": organisation,
                "retailer_group": retailer_group,
                "passes": passes,
                "date_invoice": first_day_of_previous_month,
                "date_generated": today,
                "commission_percentage": f"{retailer_group.commission_percentage}%",
                "commission_amount": f"${commission_amount}",
                "total_sales": f"${total_sales}",
                "total_payable": f"${total_payable}",
            }
            invoice_template_docx.render(context)
            invoice_filename = f"Park Passes Invoice - {retailer_group.name} - {first_day_of_previous_month.date()} "
            invoice_filename += f"{last_day_of_previous_month.date()}.docx"
            invoice_path = f"{settings.RETAILER_GROUP_INVOICE_ROOT}/{slugify(retailer_group.name)}/{invoice_filename}"
            Path(
                f"{settings.RETAILER_GROUP_INVOICE_ROOT}/{slugify(retailer_group.name)}"
            ).mkdir(parents=True, exist_ok=True)
            invoice_template_docx.save(invoice_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--convert-to",
                    "pdf",
                    invoice_path,
                    "--outdir",
                    f"{settings.RETAILER_GROUP_INVOICE_ROOT}/{slugify(retailer_group.name)}",
                ]
            )

            passes_by_type = Pass.objects.filter(
                sold_via=retailer_group,
                datetime_created__range=(
                    first_day_of_previous_month,
                    last_day_of_previous_month,
                ),
            ).order_by("option__pricing_window__pass_type")

            # We have to build a dict of pass types and their counts and total sales
            # because getting the price after all discounts is either difficult or impossible
            # to do with the django ORM or even pure SQL
            total_sales_by_pass_type_dict = {}
            for park_pass in passes_by_type:
                pass_type = park_pass.option.pricing_window.pass_type.display_name
                if pass_type not in total_sales_by_pass_type_dict:
                    total_sales_by_pass_type_dict[pass_type] = {}
                    total_sales_by_pass_type_dict[pass_type]["count"] = 0
                    total_sales_by_pass_type_dict[pass_type]["total_sales"] = Decimal(
                        0.00
                    )
                total_sales_by_pass_type_dict[pass_type]["count"] += 1
                total_sales_by_pass_type_dict[pass_type][
                    "total_sales"
                ] += park_pass.price_after_all_discounts

            logger.info(f"sales by pass type dict: {total_sales_by_pass_type_dict}")

            context = {
                "organisation": organisation,
                "rg": retailer_group,
                "total_sales_by_pass_type_dict": total_sales_by_pass_type_dict,
                "date_report": first_day_of_previous_month,
                "date_generated": today,
                "commission_percentage": f"{retailer_group.commission_percentage}%",
                "commission_amount": f"${commission_amount}",
                "total_sales": f"${total_sales}",
                "total_payable": f"${total_payable}",
            }
            report_template_docx.render(context)
            report_filename = f"Park Passes Report - {retailer_group.name} - {first_day_of_previous_month.date()} "
            report_filename += f"{last_day_of_previous_month.date()}.docx"
            report_path = f"{settings.RETAILER_GROUP_REPORT_ROOT}/{slugify(retailer_group.name)}/{report_filename}"
            Path(
                f"{settings.RETAILER_GROUP_REPORT_ROOT}/{slugify(retailer_group.name)}"
            ).mkdir(parents=True, exist_ok=True)
            report_template_docx.save(report_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--convert-to",
                    "pdf",
                    report_path,
                    "--outdir",
                    f"{settings.RETAILER_GROUP_REPORT_ROOT}/{slugify(retailer_group.name)}",
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
            report.uuid = invoice_uuid
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
