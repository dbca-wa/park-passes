import logging
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

cron_email = logging.getLogger("cron_email")

LOGFILE = "logs/" + settings.CRON_EMAIL_FILE_NAME  # This file is used temporarily.
# It's cleared whenever this cron starts, then at the end the contents of this file is emailed.


class Command(BaseCommand):
    help = "Run the Park Passes Cron tasks"

    def handle(self, *args, **options):
        stdout_redirect = f" | tee -a {LOGFILE}"
        subprocess.call(f"cat /dev/null > {LOGFILE}", shell=True)  # empty the log file

        logger.info(f"Running command {__name__}\n\n")

        manage_script = "python manage.py"
        commands_to_run = [
            "parkpasses_check",
            "clear_expired_sessions",
            "pass_send_vehicle_details_not_provided_notification_emails",
            "pass_send_expired_notification_emails",
            "pass_send_autorenew_and_expiry_notification_emails",
            "pass_process_autorenew_payments",
            "pass_send_gold_pass_details_to_pica",
        ]
        for command in commands_to_run:
            logger.info(f"Running {manage_script} {command}\n\n")
            subprocess.call(f"{manage_script} {command}" + stdout_redirect, shell=True)

        logger.info(f"Command {__name__} completed")
        self.send_email()

    def send_email(self):
        email_instance = settings.EMAIL_INSTANCE
        contents_of_cron_email = Path(LOGFILE).read_text()
        subject = f"{settings.SYSTEM_NAME_SHORT} - Cronjob"
        to = (
            settings.CRON_NOTIFICATION_EMAIL
            if isinstance(settings.CRON_NOTIFICATION_EMAIL, list)
            else [settings.CRON_NOTIFICATION_EMAIL]
        )
        msg = EmailMultiAlternatives(
            subject,
            contents_of_cron_email,
            settings.EMAIL_FROM,
            to,
            headers={"System-Environment": email_instance},
        )
        msg.attach_alternative(contents_of_cron_email, "text/html")
        msg.send()
