from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from org_model_logs.models import CommunicationsLogEntry, EntryType
from parkpasses.components.emails.emails import TemplateEmailBase


class VoucherNotificationEmail(TemplateEmailBase):
    def __init__(self, purchaser_name):
        self.subject = "You have received a park pass voucher from {}".format(
            purchaser_name
        )
        super().__init__()

    html_template = (
        apps.get_app_config("emails").path + "/voucher_recipient_notification.html"
    )
    txt_template = (
        apps.get_app_config("emails").path + "/voucher_recipient_notification.txt"
    )


class VoucherEmails:
    default_from_email = settings.DEFAULT_FROM_EMAIL

    @classmethod
    def send_voucher_recipient_notification_email(self, voucher):
        purchaser = voucher.get_purchaser()
        email = VoucherNotificationEmail(purchaser.get_full_name())
        context = {
            "voucher": voucher,
            "purchaser": purchaser,
            "site_url": settings.SITE_URL,
        }
        message = email.send(voucher.recipient_email, context=context)
        content_type = ContentType.objects.get_for_model(voucher)
        entry_type = EntryType.objects.get()
        communication_log_kwargs = {
            "content_type": content_type,
            "object_id": str(voucher.id),
            "to": voucher.recipient_email,
            "fromm": self.default_from_email,
            "entry_type": entry_type,
            "subject": message.subject,
            "text": message.text,
            "staff": self.default_from_email,
        }
        CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
