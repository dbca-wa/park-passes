"""
This management commands sends emails to users that have one or more passes set to autorenew
in future and yet they have no primary card set up in ledger.

Usage: ./manage.sh pass_send_no_primary_card_for_autorenewal
        (this command should be run by a cron job or task runner not manually)

"""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger_api_client import utils

from parkpasses.components.passes.models import Pass

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends emails to notify users that they need to set up a primary card for autorenewal payments."

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Adding the test flag will output what emails would be sent without actually sending them.",
        )

    def handle(self, *args, **options):
        logger.info(f"Running {__name__}")
        today = timezone.now()
        pass_expiry_datetime = today + timezone.timedelta(
            days=settings.PASS_REMINDER_DAYS_PRIOR
        )
        pass_expiry_date = pass_expiry_datetime.date()
        logger.info(
            f"Retrieving passes that expire in {settings.PASS_REMINDER_DAYS_PRIOR} days."
        )
        passes_to_autorenew = Pass.objects.exclude(
            processing_status=Pass.CANCELLED,  # to exclude cancelled passes
        ).filter(
            in_cart=False,
            date_expiry__gt=pass_expiry_date,
            renew_automatically=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(passes_to_autorenew)} park passes that are due to be autorenewed at some point in future."
            )
        )
        if passes_to_autorenew.exists():
            for park_pass in passes_to_autorenew:
                if options["test"]:
                    if park_pass.user:
                        primary_card_resp = utils.get_primary_card_token_for_user(
                            park_pass.user
                        )
                        try:
                            ledger_payment_token_id = int(
                                primary_card_resp["primary_card"]
                            )
                            logger.info(
                                f"User {park_pass.user} has a primary card set up."
                                f" Ledger payment token id: {ledger_payment_token_id}"
                            )
                        except (KeyError, ValueError):
                            logger.info(
                                f"User {park_pass.user} has no primary card set up."
                            )
                else:
                    if park_pass.user:
                        primary_card_resp = utils.get_primary_card_token_for_user(
                            park_pass.user
                        )
                        try:
                            ledger_payment_token_id = int(
                                primary_card_resp["primary_card"]
                            )
                            logger.info(
                                f"User {park_pass.user} has a primary card set up."
                                f" Ledger payment token id: {ledger_payment_token_id}"
                            )
                        except (KeyError, ValueError):
                            logger.info(
                                f"User {park_pass.user} has no primary card set up."
                            )
                            park_pass.send_no_primary_card_for_autorenewal_email()
