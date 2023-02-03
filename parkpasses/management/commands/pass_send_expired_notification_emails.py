"""
This management commands sends emails to customers who have have a pass that expired today.

Usage: ./manage.sh pass_send_expired_notification_emails
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
        today = timezone.now().date()
        passes_that_expired_today = Pass.objects.exclude(
            processing_status=Pass.CANCELLED,
        ).filter(
            in_cart=False,
            date_expiry=today,
        )
        if passes_that_expired_today.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(passes_that_expired_today)} park passes that expired today."
                )
            )
            for park_pass in passes_that_expired_today:
                if options["test"]:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"TEST: pretending to call send_expired_notification_emails on Pass: {park_pass}"
                        )
                    )
                else:
                    park_pass.send_expired_notification_email()
                    logger.info(f"Expiry notification email sent for Pass: {park_pass}")
