import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from parkpasses.components.approvals.email import (
    send_approval_renewal_email_notification,
)
from parkpasses.components.approvals.models import Approval
from parkpasses.components.main.models import ApplicationType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send Approval renewal notice when approval is due to expire in 90 days (Excludes E Class licences)"

    def handle(self, *args, **options):
        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        expiry_notification_date = today + timedelta(days=90)
        renewal_conditions = {
            "expiry_date__lte": expiry_notification_date,
            "renewal_sent": False,
            "replaced_by__isnull": True,
        }
        logger.info(f"Running command {__name__}")

        # 2 month licences cannot be renewed
        exclude_application_types = [
            ApplicationType.FILMING,
            ApplicationType.EVENT,
            ApplicationType.ECLASS,
        ]
        queryset = (
            Approval.objects.filter(**renewal_conditions)
            .exclude(
                current_proposal__other_details__preferred_licence_period="2_months"
            )
            .exclude(
                current_proposal__application_type__name__in=exclude_application_types
            )
        )
        logger.info(f"{queryset}")
        for a in queryset:
            if a.status == "current" or a.status == "suspended":
                try:
                    a.generate_renewal_doc()
                    send_approval_renewal_email_notification(a)
                    a.renewal_sent = True
                    a.save()
                    logger.info(f"Renewal notice sent for Approval {a.id}")
                    updates.append(a.lodgement_number)
                except Exception as e:
                    err_msg = "Error sending renewal notice for Approval {}".format(
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
