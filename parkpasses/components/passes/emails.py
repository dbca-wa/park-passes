import logging

from django.apps import apps
from django.conf import settings

from parkpasses.components.emails.emails import TemplateEmailBase
from parkpasses.components.main.utils import log_communication

logger = logging.getLogger(__name__)


class PassAutoRenewNotificationEmail(TemplateEmailBase):
    subject = "Park Pass AutoRenewal Notification"
    html_template = "parkpasses/emails/pass_autorenew_notification.html"
    txt_template = "parkpasses/emails/pass_autorenew_notification.txt"


class PassExpiryNotificationEmail(TemplateEmailBase):
    subject = "Your Park Pass is Expiring Soon"
    html_template = "parkpasses/emails/pass_expiry_notification.html"
    txt_template = "parkpasses/emails/pass_expiry_notification.txt"


class PassPurchasedNotificationEmail(TemplateEmailBase):
    subject = "Your Park Pass is Ready"
    html_template = "parkpasses/emails/pass_purchased_notification.html"
    txt_template = "parkpasses/emails/pass_purchased_notification.txt"


class PassVehicleDetailsNotYetProvidedNotificationEmail(TemplateEmailBase):
    subject = "Your Park Pass still has no Vehicle Registration Numbers Attached"
    html_template = (
        "parkpasses/emails/pass_vehicle_details_not_yet_provided_notification.html"
    )
    txt_template = (
        "parkpasses/emails/pass_vehicle_details_not_yet_provided_notification.txt"
    )


class PassEmails:
    @classmethod
    def send_pass_autorenew_notification_email(self, park_pass):
        email = PassAutoRenewNotificationEmail()
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
