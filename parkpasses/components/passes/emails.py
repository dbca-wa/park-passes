import logging
import os

from django.conf import settings

from parkpasses.components.emails.emails import TemplateEmailBase
from parkpasses.components.main.utils import log_communication

logger = logging.getLogger(__name__)


class PassExpiryNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your Park Pass is Expiring Soon"
        self.html_template = "parkpasses/emails/pass_expiry_notification.html"
        self.txt_template = "parkpasses/emails/pass_expiry_notification.txt"


class PassExpiredNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your Park Pass Has Expired"
        self.html_template = "parkpasses/emails/pass_expired_notification.html"
        self.txt_template = "parkpasses/emails/pass_expired_notification.txt"


class PassPurchasedNotificationEmail(TemplateEmailBase):
    def __init__(self):
        self.subject = "Your Park Pass is Ready"
        self.html_template = "parkpasses/emails/pass_purchased_notification.html"
        self.txt_template = "parkpasses/emails/pass_purchased_notification.txt"


class PassCreatedPersonnelNotificationEmail(TemplateEmailBase):
    def __init__(self):
        self.subject = "DBCA has issued you with a Personnel Park Pass"
        self.html_template = (
            "parkpasses/emails/pass_created_personnel_notification.html"
        )
        self.txt_template = "parkpasses/emails/pass_created_personnel_notification.txt"


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


class NoPrimaryCardForAutoRenewalEmail(TemplateEmailBase):
    def __init__(self):
        self.subject = "Park Pass No Primary Card Set Up for AutoRenewal Notification"
        self.html_template = (
            "parkpasses/emails/pass_no_primary_card_for_autorenewal.html"
        )
        self.txt_template = "parkpasses/emails/pass_no_primary_card_for_autorenewal.txt"


class PassAutoRenewNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Park Pass AutoRenewal Notification"
        self.html_template = "parkpasses/emails/pass_autorenew_notification.html"
        self.txt_template = "parkpasses/emails/pass_autorenew_notification.txt"


class PassAutoRenewSuccessNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Park Pass AutoRenewal Success Notification"
        self.html_template = (
            "parkpasses/emails/pass_autorenew_success_notification.html"
        )
        self.txt_template = "parkpasses/emails/pass_autorenew_success_notification.txt"


class PassAutoRenewFailureNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Park Pass AutoRenewal Failure Notification"
        self.html_template = (
            "parkpasses/emails/pass_autorenew_failure_notification.html"
        )
        self.txt_template = "parkpasses/emails/pass_autorenew_failure_notification.txt"


class PassFinalAutoRenewFailureNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Park Pass Final AutoRenewal Failure Notification"
        self.html_template = (
            "parkpasses/emails/pass_final_autorenew_failure_notification.html"
        )
        self.txt_template = (
            "parkpasses/emails/pass_final_autorenew_failure_notification.txt"
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
        if settings.PERSONNEL_PASS == park_pass.option.pricing_window.pass_type.name:
            email = PassCreatedPersonnelNotificationEmail()
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
    def send_pass_expired_notification_email(self, park_pass):
        email = PassExpiredNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_no_primary_card_for_autorenewal_email(self, park_pass):
        email = NoPrimaryCardForAutoRenewalEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_autorenew_notification_email(self, park_pass):
        email = PassAutoRenewNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        next_renewal_option = park_pass.get_next_renewal_option
        context = {
            "pass": serializer.data,
            "next_renewal_option": next_renewal_option,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_autorenew_success_notification_email(self, park_pass):
        email = PassAutoRenewSuccessNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_autorenew_failure_notification_email(self, park_pass, failure_count):
        email = PassAutoRenewFailureNotificationEmail()
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(park_pass)
        context = {
            "pass": serializer.data,
            "failure_count": failure_count,
            "site_url": settings.SITE_URL,
        }
        message = email.send(park_pass.email, context=context)
        log_communication(park_pass.email, message, "email", park_pass)

    @classmethod
    def send_pass_final_autorenew_failure_notification_email(self, park_pass):
        email = PassFinalAutoRenewFailureNotificationEmail()
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
        email = PassGoldPassDetailsForPICAEmail(date.strftime("%d/%m/%Y"))
        from parkpasses.components.passes.serializers import ExternalPassSerializer

        serializer = ExternalPassSerializer(passes, many=True)
        context = {
            "passes": serializer.data,
            "site_url": settings.SITE_URL,
        }
        attachments = []
        with open(gold_passes_excel_file_path, encoding="ISO-8859-1") as f:
            content = f.read()
        file_name = os.path.basename(gold_passes_excel_file_path)
        attachment = (
            file_name,
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        attachments.append(attachment)
        email.send(settings.PICA_EMAIL, context=context, attachments=attachments)
