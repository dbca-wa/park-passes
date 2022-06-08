import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.accounts.models import EmailUser

from parkpasses.components.approvals.models import Approval

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Change the status of Approvals to Expired when past expiry date"

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password="")

        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        logger.info(f"Running command {__name__}")
        # for a in Approval.objects.filter(status='current'):
        for a in Approval.objects.filter(status="current", replaced_by__isnull=True):
            if a.expiry_date < today:
                try:
                    a.expire_approval(user)
                    a.save()
                    logger.info(f"Updated Approval {a.id} status to {a.status}")
                    updates.append(a.lodgement_number)
                except Exception as e:
                    err_msg = "Error updating Approval {} status".format(
                        a.lodgement_number
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
