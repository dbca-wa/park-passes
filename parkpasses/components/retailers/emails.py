import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from org_model_logs.models import CommunicationsLogEntry, EntryType

from parkpasses.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)


class RetailerGroupUserInviteNotificationEmail(TemplateEmailBase):
    def __init__(self, SYSTEM_NAME, retailer_group_name):
        super().__init__()
        self.subject = f"You have been invited to the { SYSTEM_NAME } Retailer Group {retailer_group_name}"
        self.html_template = (
            "parkpasses/emails/retailer/retailer_group_user_invite.html"
        )
        self.txt_template = "parkpasses/emails/retailer/retailer_group_user_invite.txt"


class RetailerGroupUserAcceptedNotificationEmail(TemplateEmailBase):
    def __init__(self, email, retailer_group_name):
        super().__init__()
        self.subject = f"Retailer Group User {email} has accepted invite to {retailer_group_name} Retailer Group"
        self.html_template = (
            "parkpasses/emails/internal/retailer_group_user_invite_accepted.html"
        )
        self.txt_template = (
            "parkpasses/emails/internal/retailer_group_user_invite_accepted.txt"
        )


class RetailerGroupUserApprovedNotificationEmail(TemplateEmailBase):
    def __init__(self, SYSTEM_NAME, retailer_group_name):
        super().__init__()
        self.subject = f"Your invite to the { SYSTEM_NAME } Retailer Group {retailer_group_name} has been Approved"
        self.html_template = (
            "parkpasses/emails/retailer/retailer_group_user_invite_approved.html"
        )
        self.txt_template = (
            "parkpasses/emails/retailer/retailer_group_user_invite_approved.txt"
        )


class RetailerGroupUserDeniedNotificationEmail(TemplateEmailBase):
    def __init__(self, SYSTEM_NAME, retailer_group_name):
        super().__init__()
        self.subject = f"Your invite to the { SYSTEM_NAME } Retailer Group {retailer_group_name} has been Denied"
        self.html_template = (
            "parkpasses/emails/retailer/retailer_group_user_invite_denied.html"
        )
        self.txt_template = (
            "parkpasses/emails/retailer/retailer_group_user_invite_denied.txt"
        )


class RetailerEmails:
    @classmethod
    def send_retailer_group_user_invite_notification_email(
        self, retailer_group_user_invite
    ):
        email = RetailerGroupUserInviteNotificationEmail(
            settings.SYSTEM_NAME, retailer_group_user_invite.retailer_group__name
        )
        context = {
            "SYSTEM_NAME": settings.SYSTEM_NAME,
            "retailer_group_user_invite": retailer_group_user_invite,
        }
        message = email.send(retailer_group_user_invite.email, context=context)
        if message:
            content_type = ContentType.objects.get_for_model(retailer_group_user_invite)
            entry_type = EntryType.objects.get(entry_type__iexact="email")
            staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
            communication_log_kwargs = {
                "content_type": content_type,
                "object_id": str(retailer_group_user_invite.id),
                "to": retailer_group_user_invite.email,
                "fromm": settings.DEFAULT_FROM_EMAIL,
                "entry_type": entry_type,
                "subject": message.subject,
                "text": message.body,
                "staff": staff.id,
            }
            CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
        return message

    def send_retailer_group_user_accepted_notification_email(
        self, retailer_group_user_invite
    ):
        email = RetailerGroupUserAcceptedNotificationEmail(
            retailer_group_user_invite.email,
            retailer_group_user_invite.retailer_group__name,
        )
        context = {
            "ADMIN_GROUP": settings.ADMIN_GROUP,
            "retailer_group_user_invite": retailer_group_user_invite,
        }
        message = email.send(retailer_group_user_invite.email, context=context)
        if message:
            content_type = ContentType.objects.get_for_model(retailer_group_user_invite)
            entry_type = EntryType.objects.get(entry_type__iexact="email")
            staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
            communication_log_kwargs = {
                "content_type": content_type,
                "object_id": str(retailer_group_user_invite.id),
                "to": retailer_group_user_invite.email,
                "fromm": settings.DEFAULT_FROM_EMAIL,
                "entry_type": entry_type,
                "subject": message.subject,
                "text": message.body,
                "customer": retailer_group_user_invite.user,
                "staff": staff.id,
            }
            CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
        return message

    def send_retailer_group_user_approved_notification_email(
        self, retailer_group_user_invite
    ):
        email = RetailerGroupUserApprovedNotificationEmail(
            settings.SYSTEM_NAME, retailer_group_user_invite.retailer_group__name
        )
        context = {
            "SYSTEM_NAME": settings.SYSTEM_NAME,
            "retailer_group_user_invite": retailer_group_user_invite,
        }
        message = email.send(retailer_group_user_invite.email, context=context)
        if message:
            content_type = ContentType.objects.get_for_model(retailer_group_user_invite)
            entry_type = EntryType.objects.get(entry_type__iexact="email")
            staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
            communication_log_kwargs = {
                "content_type": content_type,
                "object_id": str(retailer_group_user_invite.id),
                "to": retailer_group_user_invite.email,
                "fromm": settings.DEFAULT_FROM_EMAIL,
                "entry_type": entry_type,
                "subject": message.subject,
                "text": message.body,
                "customer": retailer_group_user_invite.user,
                "staff": staff.id,
            }
            CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
            return message

    def send_retailer_group_user_denied_notification_email(
        self, retailer_group_user_invite
    ):
        email = RetailerGroupUserDeniedNotificationEmail(
            settings.SYSTEM_NAME, retailer_group_user_invite.retailer_group__name
        )
        context = {
            "SYSTEM_NAME": settings.SYSTEM_NAME,
            "retailer_group_user_invite": retailer_group_user_invite,
        }
        message = email.send(retailer_group_user_invite.email, context=context)
        if message:
            content_type = ContentType.objects.get_for_model(retailer_group_user_invite)
            entry_type = EntryType.objects.get(entry_type__iexact="email")
            staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
            communication_log_kwargs = {
                "content_type": content_type,
                "object_id": str(retailer_group_user_invite.id),
                "to": retailer_group_user_invite.email,
                "fromm": settings.DEFAULT_FROM_EMAIL,
                "entry_type": entry_type,
                "subject": message.subject,
                "text": message.body,
                "customer": retailer_group_user_invite.user,
                "staff": staff.id,
            }
            CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
        return message
