"""
This management commands generates reports and invoices for each retailer for the previous month

Usage: ./manage.sh retailers_generate_monthly_invoices
        (this command should be run on the 1st day of every month by a cron job or task runner not manually)

"""
import logging
import os
import subprocess
import uuid
from collections import namedtuple
from decimal import Decimal
from pathlib import Path

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from docxtpl import DocxTemplate
from ledger_api_client import utils as ledger_api_client_utils

from parkpasses.components.cart.utils import CartUtils
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
            help=(
                "Add the test flag will use the current month instead of the previous month "
                "and will output what emails would be sent without actually sending them."
            ),
        )

    def handle(self, *args, **options):
        organisation = settings.ORGANISATION
        report_template_docx = DocxTemplate(
            "parkpasses/management/templates/RetailerGroupReportTemplate.docx"
        )
        statement_template_docx = DocxTemplate(
            "parkpasses/management/templates/RetailerGroupStatementTemplate.docx"
        )
        # Because django and postgress dates are all UTC and we run this command on the 1st of the month
        # at midnight in Perth local time. We need to add 8 hours to the utc time for the following date
        # calculations to work correctly.
        perth_now = timezone.now() + timezone.timedelta(hours=8)

        # Gets the first day of the local calendar month at midnight
        today = perth_now.replace(hour=0, minute=0, second=0, microsecond=0)

        first_day_of_this_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_this_month - timezone.timedelta(
            days=1
        )

        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        # Set the time to the end of the day for the last day of the month so the query captures all
        # purchases for the month
        last_day_of_previous_month = last_day_of_previous_month.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        if options["test"]:
            first_day_of_previous_month = first_day_of_this_month
            last_day_of_previous_month = first_day_of_this_month + relativedelta(day=31)
            last_day_of_previous_month = last_day_of_previous_month.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

        self.stdout.write(
            f"\nGenerating Reports for date range: {first_day_of_previous_month} to {last_day_of_previous_month}\n\n"
        )

        # We exclude the internal retailers from these reports by
        # filtering out the retailer groups that have a null or empty commission_oracle_code
        # and those that have a commission_percentage of 0
        retailer_groups = (
            RetailerGroup.objects.exclude(
                commission_oracle_code__isnull=True,
            )
            .exclude(commission_oracle_code__exact="")
            .exclude(commission_percentage=0)
            .exclude(
                ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
            )
        )

        for retailer_group in retailer_groups:
            admin_users = retailer_group.retailer_group_users.filter(
                active=True, is_admin=True
            )
            if 0 == admin_users.count():
                logger.critical(
                    f"Unable to generate monthly invoice for retailer group: {retailer_group}"
                    " as there is no admin user to add to the invoice for this retailer group."
                )
                continue
            retailer_group_user = admin_users.first()
            email_user = retailer_group_user.emailuser
            self.stdout.write(f"\tGenerating Invoice for {retailer_group}")
            passes = Pass.objects.filter(
                sold_via=retailer_group,
                datetime_created__range=(
                    first_day_of_previous_month,
                    last_day_of_previous_month,
                ),
            ).order_by("datetime_created")

            pass_count = passes.count()
            self.stdout.write(f"\t -- Found {pass_count} Passes.\n\n")

            if 0 == pass_count:
                continue

            invoice_uuid = uuid.uuid4()

            pass_content_type = ContentType.objects.get_for_model(Pass)

            MockRequest = namedtuple("MockRequest", ["user"])
            request = MockRequest(user=email_user)

            total_sales = Decimal(0.00)
            ledger_order_lines = []
            for park_pass in passes:
                ledger_description = CartUtils.get_pass_purchase_description(park_pass)
                price_incl_tax = park_pass.price_after_all_discounts
                if settings.DEBUG:
                    # If in dev round the amounts so the payment gateway will work
                    price_incl_tax = int(price_incl_tax)
                    ledger_description += " (Price rounded for dev env)"

                ledger_order_lines.append(
                    {
                        "ledger_description": ledger_description,
                        "quantity": 1,
                        "price_excl_tax": str(price_incl_tax),
                        "price_incl_tax": str(price_incl_tax),
                        "oracle_code": CartUtils.get_oracle_code(
                            request, pass_content_type, park_pass.id
                        ),
                        "line_status": settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS,
                    }
                )
                total_sales += park_pass.price_after_concession_applied.quantize(
                    Decimal("0.01")
                )

            total_sales = total_sales.quantize(Decimal("0.01"))

            if total_sales <= Decimal(0.00):
                # No need to generate an invoice for this retailer group
                continue

            invoice_month = first_day_of_previous_month.strftime("%B")
            invoice_year = first_day_of_previous_month.strftime("%Y")

            commission_amount = (
                Decimal(total_sales / 100).quantize(Decimal("0.01"))
                * retailer_group.commission_percentage
            )
            commission_ledger_description = (
                f"{retailer_group.commission_percentage}% "
                f"Commission on Sales for the Month of {invoice_month} {invoice_year}"
            )
            if settings.DEBUG:
                # If in dev round the amounts so the payment gateway will work
                commission_amount = int(commission_amount)
                commission_amount = Decimal(commission_amount).quantize(Decimal("0.01"))
                ledger_description += " (Price rounded for dev env)"
                commission_ledger_description += " (Price rounded for dev env)"

            ledger_order_lines.append(
                {
                    "ledger_description": commission_ledger_description,
                    "quantity": 1,
                    "price_excl_tax": str(-abs(commission_amount)),
                    "price_incl_tax": str(-abs(commission_amount)),
                    "oracle_code": retailer_group.commission_oracle_code,
                    "line_status": settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS,
                },
            )
            booking_reference = invoice_uuid

            total_payable = Decimal(total_sales - commission_amount).quantize(
                Decimal("0.01")
            )

            if not settings.RETAILER_INVOICE_GENERATION_DISABLED:
                # Here we will generate the ledger invoices with Jason's new API
                request = ledger_api_client_utils.FakeRequestSessionObj()
                request.user = email_user

                basket_params = {
                    "products": ledger_order_lines,
                    "vouchers": [],
                    "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
                    "tax_override": True,
                    "custom_basket": True,
                    "booking_reference": str(booking_reference),
                    "no_payment": True,
                    "organisation": retailer_group.ledger_organisation,
                }

                basket_hash = ledger_api_client_utils.create_basket_session(
                    request, request.user.id, basket_params
                )
                basket_hash = basket_hash.split("|")[0]
                invoice_text = (
                    f"Park Pass Sales for the Month of {invoice_month} {invoice_year}"
                )
                return_preload_url = (
                    f"{settings.PARKPASSES_EXTERNAL_URL}"
                    f"/api/reports/ledger-api-retailer-invoice-success-callback/{invoice_uuid}"
                )

                future_invoice = ledger_api_client_utils.process_create_future_invoice(
                    basket_hash, invoice_text, return_preload_url
                )

                logger.info(future_invoice)

                if 200 != future_invoice["status"]:
                    logger.error(
                        f"Failed to create future invoice for {retailer_group} with basket_hash "
                        f"{basket_hash}, invoice_text {invoice_text}, return_preload_url {return_preload_url}"
                    )
                    continue

                data = future_invoice["data"]

                order_number = data["order"]
                basket_id = data["basket_id"]
                invoice_reference = data["invoice"]

            # Generate the retailer statement so the business can manually create the oracle invoice from it. haha :-(
            context = {
                "organisation": organisation,
                "rg": retailer_group,
                "passes": passes,
                "date_statement": first_day_of_previous_month,
                "date_generated": today,
                "commission_percentage": f"{retailer_group.commission_percentage}%",
                "commission_amount": f"${commission_amount}",
                "total_sales": f"${total_sales}",
                "total_payable": f"${total_payable}",
            }
            statement_template_docx.render(context)
            organisation_name = retailer_group.organisation["organisation_name"]
            statement_filename = f"Park Passes Statement - {organisation_name} - {first_day_of_previous_month.date()} "
            statement_filename += f"{last_day_of_previous_month.date()}.docx"
            statement_path = (
                f"{settings.RETAILER_GROUP_STATEMENT_ROOT}/"
                f"{slugify(organisation_name)}/{statement_filename}"
            )
            Path(
                f"{settings.RETAILER_GROUP_STATEMENT_ROOT}/{slugify(organisation_name)}"
            ).mkdir(parents=True, exist_ok=True)
            statement_template_docx.save(statement_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    statement_path,
                    "--outdir",
                    f"{settings.RETAILER_GROUP_STATEMENT_ROOT}/{slugify(organisation_name)}",
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
            organisation_name = retailer_group.organisation["organisation_name"]
            report_filename = f"Park Passes Report - {organisation_name} - {first_day_of_previous_month.date()} "
            report_filename += f"{last_day_of_previous_month.date()}.docx"
            report_path = f"{settings.RETAILER_GROUP_REPORT_ROOT}/{slugify(organisation_name)}/{report_filename}"
            Path(
                f"{settings.RETAILER_GROUP_REPORT_ROOT}/{slugify(organisation_name)}"
            ).mkdir(parents=True, exist_ok=True)
            report_template_docx.save(report_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    report_path,
                    "--outdir",
                    f"{settings.RETAILER_GROUP_REPORT_ROOT}/{slugify(organisation_name)}",
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
                if not settings.RETAILER_INVOICE_GENERATION_DISABLED:
                    report = Report.objects.create(
                        retailer_group=retailer_group,
                        uuid=invoice_uuid,
                        order_number=order_number,
                        basket_id=basket_id,
                        invoice_reference=invoice_reference,
                    )
                else:
                    # If a ledger invoice is not being generated, we can't know the processing status
                    # as the invoice will be created in oracle manually
                    report = Report.objects.create(
                        retailer_group=retailer_group,
                        processing_status=Report.INDETERMINATE,
                    )
            report.report.name = report_path.replace("docx", "pdf")
            report.statement.name = statement_path.replace("docx", "pdf")
            report.save()

            os.remove(report_path)
            os.remove(statement_path)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\tGenerated Report: {os.path.basename(report.report.name)}\n"
                )
            )
