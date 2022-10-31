"""
This management commands sends emails to customers who have have a pass that is about
to become active but have not provided any vehicle registration numbers for the pass.

Usage: ./manage.sh pass_send_vehicle_details_not_provided_notification_emails
        (this command should be run by a cron job or task runner not manually)

"""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.functions import Trim
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.passes.models import Pass

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends emails to remind users to provide vehicle details for their pass."

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
        today = timezone.now()
        pass_start_datetime = today + timezone.timedelta(
            days=settings.PASS_VEHICLE_REGO_REMINDER_DAYS_PRIOR
        )
        pass_start_date = pass_start_datetime.date()
        # Don't bother doing more expensive query if there are no passes that satisfy the basic criteria
        if (
            Pass.objects.exclude(
                cancellation__isnull=False,  # to exclude cancelled passes
            )
            .filter(
                in_cart=False,
                date_start=pass_start_date,
            )
            .exists()
        ):
            passes = (
                Pass.objects.alias(
                    vehicle_registration_1_trimmed=Trim("vehicle_registration_1"),
                    vehicle_registration_2_trimmed=Trim("vehicle_registration_2"),
                )
                .exclude(
                    processing_status=Pass.CANCELLED,  # to exclude cancelled passes
                )
                .filter(
                    in_cart=False,
                    date_start=pass_start_date,
                )
                .filter(
                    Q(
                        Q(vehicle_registration_1__isnull=True)
                        | Q(vehicle_registration_1_trimmed="")
                        & Q(vehicle_registration_2__isnull=True)
                        | Q(vehicle_registration_2_trimmed="")
                    ),
                )
            )
            if options["test"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(passes)} "
                        + f"park passes without any vehicle rego that are due to start on {pass_start_date}"
                    )
                )
            for park_pass in passes:
                if options["test"]:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "TEST: pretending to call "
                            + f"send_vehicle_details_not_provided_notification_emails on Pass: {park_pass}"
                        )
                    )
                else:
                    park_pass.send_vehicle_details_not_provided_notification_emails()
                    logger.info(
                        f"Notification email sent to recipient of Pass: {park_pass}"
                    )
                    park_pass.send_vehicle_details_not_provided_notification_emails()
                    logger.info(
                        f"Notification email sent to purchaser of Pass: {park_pass}"
                    )
