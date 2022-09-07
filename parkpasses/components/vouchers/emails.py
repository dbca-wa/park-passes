import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from org_model_logs.models import CommunicationsLogEntry, EntryType
from parkpasses.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)


class VoucherSentPurchaserNotificationEmail(TemplateEmailBase):
    subject = "Park Pass Voucher Sent"
    html_template = "parkpasses/emails/voucher_purchaser_notification.html"
    txt_template = "parkpasses/emails/voucher_purchaser_notification.txt"


class VoucherRecipientNotificationEmail(TemplateEmailBase):
    def __init__(self, purchaser_name):
        self.subject = "You have received a park pass voucher from {}".format(
            purchaser_name
        )
        super().__init__()

    html_template = "parkpasses/emails/voucher_recipient_notification.html"
    txt_template = "parkpasses/emails/voucher_recipient_notification.txt"


class VoucherEmails:
    @classmethod
    def send_voucher_purchase_notification_email(self, voucher):
        purchaser = voucher.get_purchaser
        email = VoucherSentPurchaserNotificationEmail()
        context = {
            "voucher": voucher,
            "purchaser": purchaser,
        }
        message = email.send(voucher.recipient_email, context=context)
        content_type = ContentType.objects.get_for_model(voucher)
        entry_type = EntryType.objects.get(entry_type__iexact="email")
        staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
        communication_log_kwargs = {
            "content_type": content_type,
            "object_id": str(voucher.id),
            "to": voucher.recipient_email,
            "fromm": settings.DEFAULT_FROM_EMAIL,
            "entry_type": entry_type,
            "subject": message.subject,
            "text": message.body,
            "customer": purchaser.id,
            "staff": staff.id,
        }
        CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)

    @classmethod
    def send_voucher_recipient_notification_email(self, voucher):
        purchaser = voucher.get_purchaser
        email = VoucherRecipientNotificationEmail(purchaser.get_full_name())
        context = {
            "voucher": voucher,
            "purchaser": purchaser,
            "site_url": settings.SITE_URL,
        }
        message = email.send(voucher.recipient_email, context=context)
        content_type = ContentType.objects.get_for_model(voucher)
        entry_type = EntryType.objects.get(entry_type__iexact="email")
        staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
        communication_log_kwargs = {
            "content_type": content_type,
            "object_id": str(voucher.id),
            "to": voucher.recipient_email,
            "fromm": settings.DEFAULT_FROM_EMAIL,
            "entry_type": entry_type,
            "subject": message.subject,
            "text": message.body,
            "staff": staff.id,
        }
        CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
