from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkpasses.components.approvals.models import Approval, ApprovalUserAction
from parkpasses.components.proposals.models import Proposal, ProposalUserAction
from ledger.accounts.models import EmailUser
import datetime
from parkpasses.components.approvals.email import (
    send_approval_expire_email_notification,
    send_approval_cancel_email_notification,
    send_approval_suspend_email_notification,
    send_approval_reinstate_email_notification,
    send_approval_surrender_email_notification,
)

import itertools

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Change the status of Approvals to Surrender/ Cancelled/ suspended."

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password="")

        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        logger.info("Running command {}".format(__name__))
        for a in Approval.objects.filter(status="current"):
            if a.suspension_details and a.set_to_suspend:
                from_date = datetime.datetime.strptime(
                    a.suspension_details["from_date"], "%d/%m/%Y"
                )
                from_date = from_date.date()
                if from_date <= today:
                    try:
                        a.status = "suspended"
                        a.set_to_suspend = False
                        a.save()
                        send_approval_suspend_email_notification(a)
                        proposal = a.current_proposal
                        ApprovalUserAction.log_action(
                            a,
                            ApprovalUserAction.ACTION_SUSPEND_APPROVAL.format(a.id),
                            user,
                        )
                        ProposalUserAction.log_action(
                            proposal,
                            ProposalUserAction.ACTION_SUSPEND_APPROVAL.format(
                                proposal.id
                            ),
                            user,
                        )
                        logger.info(
                            "Updated Approval {} status to {}".format(a.id, a.status)
                        )
                        updates.append(dict(suspended=a.lodgement_number))
                    except Exception as e:
                        err_msg = "Error suspending Approval {} status".format(
                            a.lodgement_number
                        )
                        logger.error("{}\n{}".format(err_msg, str(e)))
                        errors.append(err_msg)

            if a.cancellation_date and a.set_to_cancel:
                if a.cancellation_date <= today:
                    try:
                        a.status = "cancelled"
                        a.set_to_cancel = False
                        a.save()
                        send_approval_cancel_email_notification(a)
                        proposal = a.current_proposal
                        ApprovalUserAction.log_action(
                            a,
                            ApprovalUserAction.ACTION_CANCEL_APPROVAL.format(a.id),
                            user,
                        )
                        ProposalUserAction.log_action(
                            proposal,
                            ProposalUserAction.ACTION_CANCEL_APPROVAL.format(
                                proposal.id
                            ),
                            user,
                        )
                        logger.info(
                            "Updated Approval {} status to {}".format(a.id, a.status)
                        )
                        updates.append(dict(cancelled=a.lodgement_number))
                    except Exception as e:
                        err_msg = "Error cancelling Approval {} status".format(
                            a.lodgement_number
                        )
                        logger.error("{}\n{}".format(err_msg, str(e)))
                        errors.append(err_msg)

            if a.surrender_details and a.set_to_surrender:
                surrender_date = datetime.datetime.strptime(
                    a.surrender_details["surrender_date"], "%d/%m/%Y"
                )
                surrender_date = surrender_date.date()
                if surrender_date <= today:
                    try:
                        a.status = "surrendered"
                        a.set_to_surrender = False
                        a.save()
                        send_approval_surrender_email_notification(a)
                        proposal = a.current_proposal
                        ApprovalUserAction.log_action(
                            a,
                            ApprovalUserAction.ACTION_SURRENDER_APPROVAL.format(a.id),
                            user,
                        )
                        ProposalUserAction.log_action(
                            proposal,
                            ProposalUserAction.ACTION_SURRENDER_APPROVAL.format(
                                proposal.id
                            ),
                            user,
                        )
                        logger.info(
                            "Updated Approval {} status to {}".format(a.id, a.status)
                        )
                        updates.append(dict(surrender=a.lodgement_number))
                    except:
                        err_msg = "Error surrendering Approval {} status".format(
                            a.lodgement_number
                        )
                        logger.error("{}\n{}".format(err_msg, str(e)))
                        errors.append(err_msg)

        for a in Approval.objects.filter(status="suspended"):
            if a.suspension_details and a.suspension_details["to_date"]:
                to_date = datetime.datetime.strptime(
                    a.suspension_details["to_date"], "%d/%m/%Y"
                )
                to_date = to_date.date()
                if to_date <= today and today < a.expiry_date:
                    try:
                        a.status = "current"
                        a.save()
                        proposal = a.current_proposal
                        ApprovalUserAction.log_action(
                            a,
                            ApprovalUserAction.ACTION_REINSTATE_APPROVAL.format(a.id),
                            user,
                        )
                        ProposalUserAction.log_action(
                            proposal,
                            ProposalUserAction.ACTION_REINSTATE_APPROVAL.format(
                                proposal.id
                            ),
                            user,
                        )
                        logger.info(
                            "Updated Approval {} status to {}".format(a.id, a.status)
                        )
                        updates.append(dict(current=a.lodgement_number))
                    except Exception as e:
                        err_msg = "Error suspending Approval {} status".format(
                            a.lodgement_number
                        )
                        logger.error("{}\n{}".format(err_msg, str(e)))
                        errors.append(err_msg)

            if a.cancellation_date and a.set_to_cancel:
                if a.cancellation_date <= today:
                    try:
                        a.status = "cancelled"
                        a.set_to_cancel = False
                        a.save()
                        send_approval_cancel_email_notification(a)
                        proposal = a.current_proposal
                        ApprovalUserAction.log_action(
                            a,
                            ApprovalUserAction.ACTION_CANCEL_APPROVAL.format(a.id),
                            user,
                        )
                        ProposalUserAction.log_action(
                            proposal,
                            ProposalUserAction.ACTION_CANCEL_APPROVAL.format(
                                proposal.id
                            ),
                            user,
                        )
                        logger.info(
                            "Updated Approval {} status to {}".format(a.id, a.status)
                        )
                        updates.append(dict(cancelled=a.lodgement_number))
                    except Exception as e:
                        err_msg = "Error cancelling Approval {} status".format(
                            a.lodgement_number
                        )
                        logger.error("{}\n{}".format(err_msg, str(e)))
                        errors.append(err_msg)

            if a.surrender_details and a.set_to_surrender:
                surrender_date = datetime.datetime.strptime(
                    a.surrender_details["surrender_date"], "%d/%m/%Y"
                )
                surrender_date = surrender_date.date()
                if surrender_date <= today:
                    try:
                        a.status = "surrendered"
                        a.set_to_surrender = False
                        a.save()
                        send_approval_surrender_email_notification(a)
                        proposal = a.current_proposal
                        ApprovalUserAction.log_action(
                            a,
                            ApprovalUserAction.ACTION_SURRENDER_APPROVAL.format(a.id),
                            user,
                        )
                        ProposalUserAction.log_action(
                            proposal,
                            ProposalUserAction.ACTION_SURRENDER_APPROVAL.format(
                                proposal.id
                            ),
                            user,
                        )
                        logger.info(
                            "Updated Approval {} status to {}".format(a.id, a.status)
                        )
                        updates.append(dict(surrendered=a.lodgement_number))
                    except:
                        err_msg = "Error surrendering Approval {} status".format(
                            a.lodgement_number
                        )
                        logger.error("{}\n{}".format(err_msg, str(e)))
                        errors.append(err_msg)

        logger.info("Command {} completed".format(__name__))

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_str = (
            '<strong style="color: red;">Errors: {}</strong>'.format(len(errors))
            if len(errors) > 0
            else '<strong style="color: green;">Errors: 0</strong>'
        )
        msg = "<p>{} completed. Errors: {}. IDs updated: {}.</p>".format(
            cmd_name, err_str, updates
        )
        logger.info(msg)
        print(msg)  # will redirect to cron_tasks.log file, by the parent script
