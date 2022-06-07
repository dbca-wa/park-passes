import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text

# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from parkpasses.components.emails.emails import TemplateEmailBase
#from parkpasses.components.bookings.awaiting_payment_invoice_pdf import (
#    create_awaiting_payment_invoice_pdf_bytes,
#)
from datetime import datetime
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + " Automated Message"

class ReferralSendNotificationEmail(TemplateEmailBase):
   subject = 'A referral for an application has been sent to you.'
   html_template = 'parkpasses/emails/proposals/send_referral_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_referral_notification.txt'


class ReferralCompleteNotificationEmail(TemplateEmailBase):
   subject = 'A referral for an application has been completed.'
   html_template = 'parkpasses/emails/proposals/send_referral_complete_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_referral_complete_notification.txt'

class ProposalDeclineSendNotificationEmail(TemplateEmailBase):
   subject = 'Your Application has been declined.'
   html_template = 'parkpasses/emails/proposals/send_decline_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_decline_notification.txt'

class ProposalApprovalSendNotificationEmail(TemplateEmailBase):
   subject = '{} - Commercial Operations Licence Approved.'.format(settings.DEP_NAME)
   html_template = 'parkpasses/emails/proposals/send_approval_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_approval_notification.txt'

class ProposalAwaitingPaymentApprovalSendNotificationEmail(TemplateEmailBase):
   subject = '{} - Commercial Filming Application - Pending Payment.'.format(settings.DEP_NAME)
   html_template = 'parkpasses/emails/proposals/send_awaiting_payment_approval_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_awaiting_payment_approval_notification.txt'

class AmendmentRequestSendNotificationEmail(TemplateEmailBase):
   subject = '{} - Commercial Operations Incomplete application.'.format(settings.DEP_NAME)
   html_template = 'parkpasses/emails/proposals/send_amendment_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_amendment_notification.txt'

class SubmitSendNotificationEmail(TemplateEmailBase):
   subject = 'A new Application has been submitted.'
   html_template = 'parkpasses/emails/proposals/send_submit_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_submit_notification.txt'

class ExternalSubmitSendNotificationEmail(TemplateEmailBase):
   subject = '{} - Confirmation - Application submitted.'.format(settings.DEP_NAME)
   html_template = 'parkpasses/emails/proposals/send_external_submit_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_external_submit_notification.txt'

class ApproverDeclineSendNotificationEmail(TemplateEmailBase):
   #subject = 'A {} has been recommended for decline.'.format(application_type)
   html_template = 'parkpasses/emails/proposals/send_approver_decline_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_approver_decline_notification.txt'

class ApproverApproveSendNotificationEmail(TemplateEmailBase):
   #subject = 'A {} has been recommended for approval.'.format(application_type)
   html_template = 'parkpasses/emails/proposals/send_approver_approve_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_approver_approve_notification.txt'

class ApproverSendBackNotificationEmail(TemplateEmailBase):
   subject = 'An Application has been sent back by approver.'
   html_template = 'parkpasses/emails/proposals/send_approver_sendback_notification.html'
   txt_template = 'parkpasses/emails/proposals/send_approver_sendback_notification.txt'


def send_referral_email_notification(referral, recipients, request, reminder=False):
    # if referral.proposal.is_filming_application:
    #     email = ReferralFilmingSendNotificationEmail()
    #     proposed_start_date= referral.proposal.filming_activity.commencement_date
    # else:
    #     email = ReferralSendNotificationEmail()
    # email = ReferralSendNotificationEmail()
    application_type = referral.proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="A referral for a {} has been sent to you.".format(application_type),
        html_template="parkpasses/emails/proposals/send_referral_notification.html",
        txt_template="parkpasses/emails/proposals/send_referral_notification.txt",
    )
    url = request.build_absolute_uri(
        reverse(
            "internal-referral-detail",
            kwargs={"proposal_pk": referral.proposal.id, "referral_pk": referral.id},
        )
    )

    # filming_handbook_url= settings.COLS_FILMING_HANDBOOK_URL
    context = {
        "proposal": referral.proposal,
        "url": url,
        "reminder": reminder,
        "comments": referral.text,
        # 'filming_handbook_url': filming_handbook_url,
        # 'proposed_start_date': proposed_start_date,
        "filming_handbook_url": "",
        "proposed_start_date": "",
    }

    # msg = email.send(referral.referral.email, context=context)
    # recipients = list(ReferralRecipientGroup.objects.get(name=referral.email_group).members.all().values_list('email', flat=True))
    msg = email.send(recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, referral.proposal, sender=sender)
    if referral.proposal.org_applicant:
        _log_org_email(
            msg, referral.proposal.org_applicant, referral.referral, sender=sender
        )
    elif referral.proposal.ind_applicant:
        _log_user_email(
            msg, referral.proposal.ind_applicant, referral.referral, sender=sender
        )


def send_referral_complete_email_notification(referral, request):
    sent_by = retrieve_email_user(referral.sent_by)

    application_type = referral.proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="A referral for a {} has been completed.".format(application_type),
        html_template="parkpasses/emails/proposals/send_referral_complete_notification.html",
        txt_template="parkpasses/emails/proposals/send_referral_complete_notification.txt",
    )
    # email = ReferralCompleteNotificationEmail()
    email.subject = sent_by.email + ": " + email.subject
    url = request.build_absolute_uri(
        reverse(
            "internal-proposal-detail", kwargs={"proposal_pk": referral.proposal.id}
        )
    )

    context = {
        "completed_by": retrieve_email_user(referral.referral),
        "proposal": referral.proposal,
        "url": url,
        "referral_comments": referral.referral_text,
    }
    attachments = []
    if referral.document:
        file_name = referral.document._file.name
        # attachment = (file_name, doc._file.file.read(), 'image/*')
        attachment = (file_name, referral.document._file.file.read())
        attachments.append(attachment)

    msg = email.send(sent_by.email, attachments=attachments, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, referral.proposal, sender=sender)
    if referral.proposal.org_applicant:
        _log_org_email(
            msg, referral.proposal.org_applicant, referral.referral, sender=sender
        )
    elif referral.proposal.ind_applicant:
        _log_user_email(
            msg, referral.proposal.ind_applicant, referral.referral, sender=sender
        )


def send_amendment_email_notification(amendment_request, request, proposal):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="{} - Incomplete {}.".format(settings.DEP_NAME, application_type),
        html_template="parkpasses/emails/proposals/send_amendment_notification.html",
        txt_template="parkpasses/emails/proposals/send_amendment_notification.txt",
    )
    # email = AmendmentRequestSendNotificationEmail()
    # reason = amendment_request.get_reason_display()
    reason = amendment_request.reason.reason
    url = request.build_absolute_uri(
        reverse("external-proposal-detail", kwargs={"proposal_pk": proposal.id})
    )

    if "-internal" in url:
        # remove '-internal'. This email is for external submitters
        url = "".join(url.split("-internal"))

    context = {
        "proposal": proposal,
        "reason": reason,
        "amendment_request_text": amendment_request.text,
        "url": url,
    }
    all_ccs = []
    if proposal.org_applicant and proposal.org_applicant.email:
        cc_list = proposal.org_applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email, cc=all_ccs, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.ind_applicant, proposal.submitter, sender=sender)


def send_submit_email_notification(request, proposal):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="A new {} has been submitted.".format(application_type),
        html_template="parkpasses/emails/proposals/send_submit_notification.html",
        txt_template="parkpasses/emails/proposals/send_submit_notification.txt",
    )
    # email = SubmitSendNotificationEmail()
    url = request.build_absolute_uri(
        reverse("internal-proposal-detail", kwargs={"proposal_pk": proposal.id})
    )
    if "-internal" not in url:
        # add it. This email is for internal staff (assessors)
        url = "-internal.{}".format(settings.SITE_DOMAIN).join(
            url.split("." + settings.SITE_DOMAIN)
        )

    context = {"proposal": proposal, "url": url}

    msg = email.send(proposal.assessor_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    # if proposal.org_applicant:
    #    _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    # else:
    #    _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)
    return msg


def send_external_submit_email_notification(request, proposal):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="{} - Confirmation - {} submitted.".format(
            settings.DEP_NAME, application_type
        ),
        html_template="parkpasses/emails/proposals/send_external_submit_notification.html",
        txt_template="parkpasses/emails/proposals/send_external_submit_notification.txt",
    )
    # email = ExternalSubmitSendNotificationEmail()
    url = request.build_absolute_uri(
        reverse("external-proposal-detail", kwargs={"proposal_pk": proposal.id})
    )

    if "-internal" in url:
        # remove '-internal'. This email is for external submitters
        url = "".join(url.split("-internal"))

    context = {
        "proposal": proposal,
        #'submitter': proposal.submitter.get_full_name(),
        "submitter": EmailUser.objects.get(id=proposal.submitter).get_full_name(),
        "url": url,
    }
    all_ccs = []
    # if proposal.org_applicant and proposal.org_applicant.email:
    #    cc_list = proposal.org_applicant.email
    #    if cc_list:
    #        all_ccs = [cc_list]

    msg = email.send(
        EmailUser.objects.get(id=proposal.submitter).email, cc=all_ccs, context=context
    )
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    # if proposal.org_applicant:
    #    _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    # else:
    #    _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)
    return msg


# send email when Proposal is 'proposed to decline' by assessor.
def send_approver_decline_email_notification(reason, request, proposal):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="A {} has been recommended for decline.".format(application_type),
        html_template="parkpasses/emails/proposals/send_approver_decline_notification.html",
        txt_template="parkpasses/emails/proposals/send_approver_decline_notification.txt",
    )
    # email = ApproverDeclineSendNotificationEmail()
    url = request.build_absolute_uri(
        reverse("internal-proposal-detail", kwargs={"proposal_pk": proposal.id})
    )
    context = {"proposal": proposal, "reason": reason, "url": url}

    msg = email.send(proposal.approver_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        # TODO: implement logging
        # _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)
        pass


def send_approver_approve_email_notification(request, proposal):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="A {} has been recommended for approval.".format(application_type),
        html_template="parkpasses/emails/proposals/send_approver_approve_notification.html",
        txt_template="parkpasses/emails/proposals/send_approver_approve_notification.txt",
    )
    # email = ApproverApproveSendNotificationEmail()
    url = request.build_absolute_uri(
        reverse("internal-proposal-detail", kwargs={"proposal_pk": proposal.id})
    )
    context = {
        "start_date": proposal.proposed_issuance_approval.get("start_date"),
        "expiry_date": proposal.proposed_issuance_approval.get("expiry_date"),
        "details": proposal.proposed_issuance_approval.get("details"),
        "proposal": proposal,
        "url": url,
    }

    msg = email.send(proposal.approver_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.ind_applicant, proposal.submitter, sender=sender)


def send_proposal_decline_email_notification(proposal, request, proposal_decline):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="Your {} has been declined.".format(application_type),
        html_template="parkpasses/emails/proposals/send_decline_notification.html",
        txt_template="parkpasses/emails/proposals/send_decline_notification.txt",
    )
    # email = ProposalDeclineSendNotificationEmail(proposal.application_type.name_display)

    context = {
        "proposal": proposal,
    }
    cc_list = proposal_decline.cc_email
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(",")
    if proposal.org_applicant and proposal.org_applicant.email:
        all_ccs.append(proposal.org_applicant.email)

    # msg = email.send(proposal.submitter.email, bcc= all_ccs, context=context)
    msg = email.send(
        retrieve_email_user(proposal.submitter).email, bcc=all_ccs, context=context
    )
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)


def send_proposal_approver_sendback_email_notification(request, proposal):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="An {} has been sent back by approver.".format(application_type),
        html_template="parkpasses/emails/proposals/send_approver_sendback_notification.html",
        txt_template="parkpasses/emails/proposals/send_approver_sendback_notification.txt",
    )
    # email = ApproverSendBackNotificationEmail()
    url = request.build_absolute_uri(
        reverse("internal-proposal-detail", kwargs={"proposal_pk": proposal.id})
    )

    if "test-emails" in request.path_info:
        approver_comment = "This is my test comment"
    else:
        approver_comment = proposal.approver_comment

    context = {"proposal": proposal, "url": url, "approver_comment": approver_comment}

    msg = email.send(proposal.assessor_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.ind_applicant, proposal.submitter, sender=sender)


def send_proposal_approval_email_notification(proposal, request):
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="{} - {} Approved.".format(settings.DEP_NAME, application_type),
        html_template="parkpasses/emails/proposals/send_approval_notification.html",
        txt_template="parkpasses/emails/proposals/send_approval_notification.txt",
    )
    # email = ProposalApprovalSendNotificationEmail()

    cc_list = proposal.proposed_issuance_approval["cc_email"]
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(",")

    attachments = []
    licence_document = proposal.approval.licence_document._file
    if licence_document is not None:
        file_name = proposal.approval.licence_document.name
        attachment = (file_name, licence_document.file.read(), "application/pdf")
        attachments.append(attachment)

        # add requirement documents
        for requirement in proposal.requirements.exclude(is_deleted=True):
            for doc in requirement.requirement_documents.all():
                file_name = doc._file.name
                # attachment = (file_name, doc._file.file.read(), 'image/*')
                attachment = (file_name, doc._file.file.read())
                attachments.append(attachment)

    url = request.build_absolute_uri(reverse("external"))
    if "-internal" in url:
        # remove '-internal'. This email is for external submitters
        url = "".join(url.split("-internal"))
    context = {
        "proposal": proposal,
        "url": url,
    }

    msg = email.send(
        proposal.submitter.email, bcc=all_ccs, attachments=attachments, context=context
    )
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL

    email_entry = _log_proposal_email(msg, proposal, sender=sender)
    path_to_file = "{}/proposals/{}/approvals/{}".format(
        settings.MEDIA_APP_DIR, proposal.id, file_name
    )
    email_entry.documents.get_or_create(_file=path_to_file, name=file_name)

    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.ind_applicant, proposal.submitter, sender=sender)


def send_proposal_awaiting_payment_approval_email_notification(proposal, request):
    """Send External Email with attached invoice and URL link to pay by credit card"""
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject="{} - {} - Pending Payment.".format(
            settings.DEP_NAME, application_type
        ),
        html_template="parkpasses/emails/proposals/send_awaiting_payment_approval_notification.html",
        txt_template="parkpasses/emails/proposals/send_awaiting_payment_approval_notification.txt",
    )
    # email = ProposalAwaitingPaymentApprovalSendNotificationEmail()

    cc_list = proposal.proposed_issuance_approval["cc_email"]
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(",")

    url = request.build_absolute_uri(reverse("external"))
    # payment_url = request.build_absolute_uri(reverse('existing_invoice_payment', kwargs={'invoice_ref':invoice.reference}))
    if "-internal" in url:
        # remove '-internal'. This email is for external submitters
        url = "".join(url.split("-internal"))

    filename = "confirmation.pdf"
    doc = create_awaiting_payment_invoice_pdf_bytes(filename, proposal)
    attachment = (filename, doc, "application/pdf")

    context = {
        "proposal": proposal,
        "url": url,
    }

    msg = email.send(
        proposal.submitter.email, bcc=all_ccs, attachments=[attachment], context=context
    )
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL

    filename_appended = "{}_{}.{}".format(
        "confirmation", datetime.now().strftime("%d%b%Y"), "pdf"
    )
    log_proposal = _log_proposal_email(
        msg, proposal, sender=sender, file_bytes=doc, filename=filename_appended
    )

    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.ind_applicant, proposal.submitter, sender=sender)


# def _log_proposal_referral_email(email_message, referral, sender=None):
#    from parkpasses.components.proposals.models import ProposalLogEntry
#    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
#        # TODO this will log the plain text body, should we log the html instead
#        text = email_message.body
#        subject = email_message.subject
#        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
#        # the to email is normally a list
#        if isinstance(email_message.to, list):
#            to = ','.join(email_message.to)
#        else:
#            to = smart_text(email_message.to)
#        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
#        all_ccs = []
#        if email_message.cc:
#            all_ccs += list(email_message.cc)
#        if email_message.bcc:
#            all_ccs += list(email_message.bcc)
#        all_ccs = ','.join(all_ccs)
#
#    else:
#        text = smart_text(email_message)
#        subject = ''
#        to = referral.proposal.applicant.email
#        fromm = smart_text(sender) if sender else SYSTEM_NAME
#        all_ccs = ''
#
#    customer = referral.referral
#
#    staff = sender
#
#    kwargs = {
#        'subject': subject,
#        'text': text,
#        'proposal': referral.proposal,
#        'customer': customer,
#        'staff': staff.id,
#        'to': to,
#        'fromm': fromm,
#        'cc': all_ccs
#    }
#
#    email_entry = ProposalLogEntry.objects.create(**kwargs)
#
#    return email_entry


def _log_proposal_email(
    email_message, proposal, sender=None, file_bytes=None, filename=None
):
    from parkpasses.components.proposals.models import ProposalLogEntry

    if isinstance(
        email_message,
        (
            EmailMultiAlternatives,
            EmailMessage,
        ),
    ):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ",".join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ",".join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ""
        # to = proposal.submitter.email
        to = EmailUser.objects.get(id=proposal.submitter).email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""
    customer = proposal.submitter

    staff = sender.id

    kwargs = {
        "subject": subject,
        "text": text,
        "proposal": proposal,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = ProposalLogEntry.objects.create(**kwargs)

    if file_bytes and filename:
        # attach the file to the comms_log also
        path_to_file = "{}/proposals/{}/communications/{}".format(
            settings.MEDIA_APP_DIR, proposal.id, filename
        )
        path = default_storage.save(path_to_file, ContentFile(file_bytes))
        email_entry.documents.get_or_create(_file=path_to_file, name=filename)

    return email_entry


def _log_org_email(email_message, organisation, customer, sender=None):
    from parkpasses.components.organisations.models import OrganisationLogEntry

    if isinstance(
        email_message,
        (
            EmailMultiAlternatives,
            EmailMessage,
        ),
    ):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ",".join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ",".join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ""
        to = customer
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    customer = customer

    staff = sender

    kwargs = {
        "subject": subject,
        "text": text,
        "organisation": organisation,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = OrganisationLogEntry.objects.create(**kwargs)

    return email_entry


def _log_user_email(email_message, emailuser, customer, sender=None):
    return
    # TODO: implement this

    from ledger.accounts.models import EmailUserLogEntry

    if isinstance(
        email_message,
        (
            EmailMultiAlternatives,
            EmailMessage,
        ),
    ):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ",".join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ",".join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ""
        to = customer
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    customer = customer

    staff = sender

    kwargs = {
        "subject": subject,
        "text": text,
        "emailuser": emailuser,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = EmailUserLogEntry.objects.create(**kwargs)

    return email_entry
