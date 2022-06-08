import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from ledger.accounts.models import EmailUser

from parkpasses.components.compliances.models import Compliance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send notification emails for compliances which has past due dates, and also reminder notification\
    emails for those that are within the daterange prior to due_date (eg. within 14 days of due date)"

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except Exception:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password="")

        errors = []
        updates = []
        logger.info(f"Running command {__name__}")
        for c in Compliance.objects.filter(processing_status="due"):
            try:
                c.send_reminder(user)
                c.save()
                updates.append(c.lodgement_number)
            except Exception as e:
                err_msg = "Error sending Reminder Compliance {}\n{}".format(
                    c.lodgement_number, e
                )
                logger.error(f"{err_msg}\n{str(e)}")
                errors.append(err_msg)

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_str = (
            f'<strong style="color: red;">Errors: {len(errors)}</strong>'
            if len(errors) > 0
            else '<strong style="color: green;">Errors: 0</strong>'
        )
        msg = "<p>{} completed. Errors: {}. IDs updated: {}.</p>".format(
            cmd_name, err_str, updates
        )
        logger.info(msg)
        print(msg)  # will redirect to cron_tasks.log file, by the parent script
