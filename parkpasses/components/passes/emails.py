import logging
import os

from django.conf import settings

from parkpasses.components.emails.emails import TemplateEmailBase
from parkpasses.components.main.utils import log_communication

logger = logging.getLogger(__name__)


class PassAutoRenewNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Park Pass AutoRenewal Notification"
        self.html_template = "parkpasses/emails/pass_autorenew_notification.html"
        self.txt_template = "parkpasses/emails/pass_autorenew_notification.txt"


class PassExpiryNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your Park Pass is Expiring Soon"
        self.html_template = "parkpasses/emails/pass_expiry_notification.html"
        self.txt_template = "parkpasses/emails/pass_expiry_notification.txt"


class PassPurchasedNotificationEmail(TemplateEmailBase):
    def __init__(self):
        self.subject = "Your Park Pass is Ready"
        self.html_template = "parkpasses/emails/pass_purchased_notification.html"
        self.txt_template = "parkpasses/emails/pass_purchased_notification.txt"


class PassUpdatedNotificationEmail(TemplateEmailBase):
    def __init__(self):
        self.subject = "Your Park Pass has Been Updated"
        self.html_template = "parkpasses/emails/pass_updated_notification.html"
        self.txt_template = "parkpasses/emails/pass_updated_notification.txt"


class PassVehicleDetailsNotYetProvidedNotificationEmail(TemplateEmailBase):
    def __init__(self):
        self.subject = (
            "Your Park Pass still has no Vehicle Registration Numbers Attached"
        )
        self.html_template = (
            "parkpasses/emails/pass_vehicle_details_not_yet_provided_notification.html"
        )
        self.txt_template = (
            "parkpasses/emails/pass_vehicle_details_not_yet_provided_notification.txt"
        )


class PassGoldPassDetailsForPICAEmail(TemplateEmailBase):
    def __init__(self, date_sold):
        super().__init__()
        self.subject = f"Gold Star Park Passes Sold [Yesterday: {date_sold}]"
        self.html_template = (
            "parkpasses/emails/pass_send_gold_pass_details_to_pica.html"
        )
        self.txt_template = "parkpasses/emails/pass_send_gold_pass_details_to_pica.txt"


class PassEmails:
    @classmethod
    def send_pass_purchased_notification_email(self, park_pass):
        email = PassPurchasedNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        attachments = []
        park_pass_pdf_file = park_pass.park_pass_pdf.open()
        file_name = os.path.basename(park_pass_pdf_file.name)
        attachment = (file_name, park_pass_pdf_file.read(), "application/pdf")
        attachments.append(attachment)
        message = email.send(park_pass.email, context=context, attachments=attachments)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_updated_notification_email(self, park_pass):
        email = PassUpdatedNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        attachments = []
        park_pass_pdf_file = park_pass.park_pass_pdf.open()
        file_name = os.path.basename(park_pass_pdf_file.name)
        attachment = (file_name, park_pass_pdf_file.read(), "application/pdf")
        attachments.append(attachment)
        message = email.send(park_pass.email, context=context, attachments=attachments)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_vehicle_details_not_yet_provided_notification_email(self, park_pass):
        email = PassVehicleDetailsNotYetProvidedNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_expiry_notification_email(self, park_pass):
        email = PassExpiryNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_gold_pass_details_to_pica(self, date, passes, gold_passes_excel_file_path):
        logger.debug("send_gold_pass_details_to_pica")
        email = PassGoldPassDetailsForPICAEmail(date.strftime("%d/%m/%Y"))
        logger.debug(str(email))
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(passes, many=True)
        context = {
            "passes": serializer.data,
            "site_url": settings.SITE_URL,
        }
        attachments = []
        content = open(gold_passes_excel_file_path, "rb").read()
        file_name = os.path.basename(gold_passes_excel_file_path)
        attachment = (
            file_name,
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        attachments.append(attachment)
        email.send(settings.PICA_EMAIL, context=context, attachments=attachments)
        logger.debug("Email sent supposedly.")
