import logging

from django.apps import apps
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
        self.html_template = "parkpasses/emails/pass_autorenew_notification.html"
        self.txt_template = "parkpasses/emails/pass_autorenew_notification.txt"


class PassEmails:
    @classmethod
    def send_pass_purchased_notification_email(self, park_pass):
        email = PassPurchasedNotificationEmail()
        ExternalPassSerializer = apps.get_model("parkpasses", "ExternalPassSerializer")
        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.recipient_email, message, "email", park_pass)

    @classmethod
    def send_pass_updated_notification_email(self, park_pass):
        email = PassUpdatedNotificationEmail()
        ExternalPassSerializer = apps.get_model("parkpasses", "ExternalPassSerializer")
        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.recipient_email, message, "email", park_pass)

    @classmethod
    def send_pass_vehicle_details_not_yet_provided_notification_email(self, park_pass):
        email = PassVehicleDetailsNotYetProvidedNotificationEmail()
        ExternalPassSerializer = apps.get_model("parkpasses", "ExternalPassSerializer")
        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.recipient_email, message, "email", park_pass)

    @classmethod
    def send_pass_expiry_notification_email(self, park_pass):
        email = PassExpiryNotificationEmail()
        ExternalPassSerializer = apps.get_model("parkpasses", "ExternalPassSerializer")
        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.recipient_email, message, "email", park_pass)

    @classmethod
    def send_gold_pass_details_to_pica(self, park_pass, gold_passes_excel_file):
        logger.debug("send_gold_pass_details_to_pica")
        email = PassGoldPassDetailsForPICAEmail(
            park_pass.datetime_created.strftime("%d/%m/%Y")
        )
        logger.debug(str(email))
        context = {
            "park_pass": park_pass,
            "site_url": settings.SITE_URL,
        }
        message = email.send(
            park_pass.email, context=context, attachments=[gold_passes_excel_file]
        )
        log_communication(park_pass.recipient_email, message, "email", park_pass)
