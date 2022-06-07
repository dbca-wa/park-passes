from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from ledger.accounts.models import EmailUser
from parkpasses.components.compliances.models import (
    Compliance,
    ComplianceUserAction,
)
from parkpasses.components.compliances.email import (
    send_due_email_notification,
    send_internal_due_email_notification,
)
import datetime
import itertools

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Change the status of Compliances from future to due when they are close to due date"

    def handle(self, *args, **options):
        today = timezone.localtime(timezone.now()).date()
        compare_date = today + datetime.timedelta(days=14)

        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password="")

        logger.info("Running command {}".format(__name__))
        errors = []
        updates = []
        for c in Compliance.objects.filter(processing_status="future"):
            # if(c.due_date<= compare_date<= c.approval.expiry_date) and c.approval.status=='current':
            if (
                (c.due_date <= compare_date)
                and (c.due_date <= c.approval.expiry_date)
                and c.approval.status == "current"
            ):
                try:
                    c.processing_status = "due"
                    c.customer_status = "due"
                    c.save()
                    ComplianceUserAction.log_action(
                        c, ComplianceUserAction.ACTION_STATUS_CHANGE.format(c.id), user
                    )
                    logger.info(
                        "updated Compliance {} status to {}".format(
                            c.lodgement_number, c.processing_status
                        )
                    )
                    updates.append(c.lodgement_number)
                except Exception as e:
                    err_msg = "Error updating Compliance {} status".format(
                        c.lodgement_number
                    )
                    logger.error("{}\n{}".format(err_msg, str(e)))
                    errors.append(err_msg)

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_str = (
            '<strong style="color: red;">Errors: {}</strong>'.format(len(errors))
            if len(errors) > 0
            else '<strong style="color: green;">Errors: 0</strong>'
        )
        msg = "<p>{} completed. Errors: {}. IDs updated: {}.</p>".format(
            cmd_name, err_str, updates
        )
        logger.info(msg)
        print(msg)  # will redirect to cron_tasks.log file, by the parent script
