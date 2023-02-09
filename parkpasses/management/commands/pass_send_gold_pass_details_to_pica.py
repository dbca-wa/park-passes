"""
This management commands sends the details of any new gold star passes to pica so they
    can arrange for their landscope magazine subscription to be sent out.

Usage: ./manage.sh pass_send_gold_pass_details_to_pica
        (this command should be run by a cron job at 3am each day)

    When the test flag "--test" is appended the gold star passes from today will be selected
    instead of the ones from yesterday.
"""
import logging
from pathlib import Path

import xlsxwriter
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.passes.emails import PassEmails
from parkpasses.components.passes.exceptions import SendGoldPassDetailsToPICAEmailFailed
from parkpasses.components.passes.models import Pass

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends the details of any new gold star passes to pica."

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Adding the test flag will output what emails would be sent without actually sending them.",
        )

    def handle(self, *args, **options):
        no_reply_email_user, created = EmailUser.objects.get_or_create(
            email=settings.NO_REPLY_EMAIL, password=""
        )
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        date = yesterday
        if options["test"]:
            date = today

        # Don't bother doing more expensive query if there are no passes that satisfy the basic criteria
        pass_queryset = Pass.objects.exclude(
            cancellation__isnull=False,  # to exclude cancelled passes
        ).filter(
            in_cart=False,
            option__pricing_window__pass_type__name=settings.GOLD_STAR_PASS,
            datetime_created__date=date,
        )

        if pass_queryset.exists():
            passes = pass_queryset
            if options["test"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(passes)} gold star park pass(es) that were sold today."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(passes)} gold star park pass(es) that were sold yesterday."
                    )
                )

            Path(settings.PICA_GOLD_STAR_PASS_ROOT).mkdir(parents=True, exist_ok=True)

            file_path = (
                settings.PICA_GOLD_STAR_PASS_ROOT
                + f"/gold-star-pass-sales-for-pica-{slugify(yesterday)}.xlsx"
            )
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()

            bold = workbook.add_format({"bold": True})

            worksheet.write("A1", "Pass Number", bold)
            worksheet.write("B1", "First Name", bold)
            worksheet.write("C1", "Last Name", bold)
            worksheet.write("D1", "Address Line 1", bold)
            worksheet.write("E1", "Address Line 2", bold)
            worksheet.write("F1", "Suburb", bold)
            worksheet.write("G1", "Postcode", bold)
            worksheet.write("H1", "State", bold)
            worksheet.write("I1", "Mobile", bold)
            worksheet.write("J1", "Start Date of Pass", bold)

            worksheet.set_column(0, 2, 15)
            worksheet.set_column(3, 4, 30)
            worksheet.set_column(5, 9, 15)

            for row_num, data in enumerate(passes):
                worksheet.write(row_num + 1, 0, data.pass_number)
                worksheet.write(row_num + 1, 1, data.first_name)
                worksheet.write(row_num + 1, 2, data.last_name)
                worksheet.write(row_num + 1, 3, data.address_line_1)
                worksheet.write(row_num + 1, 4, data.address_line_2)
                worksheet.write(row_num + 1, 5, data.suburb)
                worksheet.write(row_num + 1, 6, data.postcode)
                worksheet.write(row_num + 1, 7, data.state)
                worksheet.write(row_num + 1, 8, data.mobile)
                worksheet.write(row_num + 1, 9, data.date_start.strftime("%d-%m-%Y"))

            workbook.close()

            error_message = "An exception occured trying to run "
            error_message += (
                "send_gold_pass_details_to_pica for Pass with id {}. Exception {}"
            )
            try:
                PassEmails.send_gold_pass_details_to_pica(date, passes, file_path)
                logger.info(
                    "Email of new Gold Pass Information sent to PICA.",
                )
            except Exception as e:
                logger.exception(e)
                raise SendGoldPassDetailsToPICAEmailFailed(
                    "There was an exception trying to send gold pass details to PICA. "
                    f"Date {date}, Passes: {passes}, File Path: {file_path}. Exception: {e}"
                )
