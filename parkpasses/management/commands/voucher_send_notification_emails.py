"""
This management commands sends emails to customers who have had a voucher purchased
for them on the date that the purchaser specified.

Usage: ./manage.sh send_voucher_recipient_notification_emails
        (this command should be run by a cron job or task runner not manually)

"""
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from parkpasses.components.vouchers.models import Voucher

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends any voucher emails that are due to be sent on the day the command is run."

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Add the test flag will output what emails would be sent without actually sending them.",
        )

    def handle(self, *args, **options):
        """First: Attempt to resend any vouchers that haven't had success being sent to the purchaser"""
        vouchers = Voucher.objects.filter(
            processing_status__in=[Voucher.NEW, Voucher.NOT_DELIVERED_TO_PURCHASER],
        )
        if options["test"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(vouchers)} vouchers that still need to be sent to the purchaser"
                )
            )
        for voucher in vouchers:
            if options["test"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"TEST: pretending to call send_voucher_purchase_notification_email on Voucher: {voucher}"
                    )
                )
            else:
                voucher.send_voucher_purchase_notification_email()
                # Save the voucher so that the processing status is updated
                voucher.save()
                logger.info(
                    f"Notification email sent to recipient and purchser of Voucher: {voucher}",
                )

        """ Second: Send any vouchers to recipients that are due to be sent today or on a
        previous day and have the appropriate processing status """
        today = timezone.now().date()
        vouchers = Voucher.objects.exclude(in_cart=True).filter(
            datetime_to_email__date__lte=today,
            processing_status__in=[
                Voucher.PURCHASER_NOTIFIED,
                Voucher.NOT_DELIVERED_TO_RECIPIENT,
            ],
        )
        if options["test"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(vouchers)} vouchers that would be sent to their recipients today {today}"
                )
            )
        for voucher in vouchers:
            if options["test"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"TEST: pretending to call send_voucher_sent_notification_emails on Voucher: {voucher}"
                    )
                )
            else:
                voucher.send_voucher_sent_notification_emails()
                # Save the voucher so that the processing status is updated
                voucher.save()
                logger.info(
                    f"Notification email sent to recipient and purchser of Voucher: {voucher}",
                )
