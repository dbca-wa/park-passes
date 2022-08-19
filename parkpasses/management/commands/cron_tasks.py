import logging
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

LOGFILE = "logs/cron_tasks.log"


class Command(BaseCommand):
    help = "Run the Commercial Operator Cron tasks"

    def handle(self, *args, **options):
        stdout_redirect = f" | tee -a {LOGFILE}"
        subprocess.call(f"cat /dev/null > {LOGFILE}", shell=True)  # empty the log file

        logger.info(f"Running command {__name__}")
        subprocess.call(
            "python manage_co.py update_compliance_status" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py send_compliance_reminder" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py update_approval_status" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py expire_approvals" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py approval_renewal_notices" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py eclass_expiry_notices" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py eclass_renewal_notices" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py monthly_invoices" + stdout_redirect, shell=True
        )
        subprocess.call(
            "python manage_co.py update_cache" + stdout_redirect, shell=True
        )

        logger.info(f"Command {__name__} completed")
        self.send_email()

    def send_email(self):
        log_txt = Path(LOGFILE).read_text()
        subject = f"{settings.SYSTEM_NAME_SHORT} - Cronjob"
        body = ""
        to = (
            settings.CRON_NOTIFICATION_EMAIL
            if isinstance(settings.NOTIFICATION_EMAIL, list)
            else [settings.CRON_NOTIFICATION_EMAIL]
        )
        send_mail(
            subject,
            body,
            settings.EMAIL_FROM,
            to,
            fail_silently=False,
            html_message=log_txt,
        )
