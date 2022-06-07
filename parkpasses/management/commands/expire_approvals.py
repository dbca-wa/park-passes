from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkpasses.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
import datetime

import itertools

import logging

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
        logger.info("Running command {}".format(__name__))
        # for a in Approval.objects.filter(status='current'):
        for a in Approval.objects.filter(status="current", replaced_by__isnull=True):
            if a.expiry_date < today:
                try:
                    a.expire_approval(user)
                    a.save()
                    logger.info(
                        "Updated Approval {} status to {}".format(a.id, a.status)
                    )
                    updates.append(a.lodgement_number)
                except Exception as e:
                    err_msg = "Error updating Approval {} status".format(
                        a.lodgement_number
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
