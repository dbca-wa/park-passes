"""
This management commands sends emails to customers who have have a pass that is about
to expire.

Usage: ./manage.sh pass_send_atuorenew_notification_emails
        (this command should be run by a cron job or task runner not manually)

"""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.passes.models import Pass

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends emails to notify users that their pass has expired."

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
        pass_expiry_datetime = today + timezone.timedelta(
            days=settings.PASS_AUTORENEW_REMINDER_DAYS_PRIOR
        )
        pass_expiry_date = pass_expiry_datetime.date()
        # Don't bother doing more expensive query if there are no passes that satisfy the basic criteria
        if (
            Pass.objects.exclude(
                cancellation__isnull=False,  # to exclude cancelled passes
            )
            .filter(
                in_cart=False,
                date_expiry=pass_expiry_date,
            )
            .exists()
        ):
            passes = Pass.objects.exclude(
                processing_status=Pass.CANCELLED,  # to exclude cancelled passes
            ).filter(
                in_cart=False,
                date_expiry=today,
            )
            if options["test"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(passes)} park passes that expire today."
                    )
                )
            for park_pass in passes:
                if options["test"]:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"TEST: pretending to call send_expiry_notification_emails on Pass: {park_pass}"
                        )
                    )
                else:
                    park_pass.send_expiry_notification_emails()
                    logger.info(
                        f"Notification email sent to recipient of Pass: {park_pass}"
                    )
