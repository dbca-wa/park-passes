from __future__ import unicode_literals

import json
import os
import datetime
import string
from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.core.validators import MaxValueValidator, MinValueValidator

# from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField, Max, Min
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings

# from ledger.accounts.models import OrganisationAddress
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, Invoice
from ledger_api_client.country_models import Country
from ledger_api_client.managed_models import SystemGroup
from parkpasses import exceptions
from parkpasses.components.main.utils import get_department_user
#from parkpasses.components.organisations.models import (
#    Organisation,
#    OrganisationContact,
#    UserDelegation,
#)
from parkpasses.components.main.models import (
    # Organisation as ledger_organisation, OrganisationAddress,
    CommunicationsLogEntry,
    UserAction,
    Document,
    ApplicationType,
    RequiredDocument,
    RevisionedMixin,
)
from parkpasses.components.proposals.email import (
    send_referral_email_notification,
    send_proposal_decline_email_notification,
    send_proposal_approval_email_notification,
    send_proposal_awaiting_payment_approval_email_notification,
    send_amendment_email_notification,
)
from parkpasses.ledger_api_utils import retrieve_email_user
from parkpasses.components.proposals.email import (
    send_submit_email_notification,
    send_external_submit_email_notification,
    send_approver_decline_email_notification,
    send_approver_approve_email_notification,
    send_referral_complete_email_notification,
    send_proposal_approver_sendback_email_notification,
)
import copy
import subprocess
from django.db.models import Q

# from reversion.models import Version
from dirtyfields import DirtyFieldsMixin
from decimal import Decimal as D
import csv
import time
from django.contrib.gis.db.models.fields import PointField, PolygonField


import logging

from parkpasses.settings import (
    APPLICATION_TYPE_REGISTRATION_OF_INTEREST,
    APPLICATION_TYPE_LEASE_LICENCE,
    GROUP_NAME_ASSESSOR,
    GROUP_NAME_APPROVER,
)

logger = logging.getLogger("parkpasses")


def update_proposal_doc_filename(instance, filename):
    return "{}/proposals/{}/documents/{}".format(
        settings.MEDIA_APP_DIR, instance.proposal.id, filename
    )


class DefaultDocument(Document):
    input_name = models.CharField(max_length=255, null=True, blank=True)
    can_delete = models.BooleanField(
        default=True
    )  # after initial submit prevent document from being deleted
    visible = models.BooleanField(
        default=True
    )  # to prevent deletion on file system, hidden and still be available in history

    class Meta:
        app_label = "parkpasses"
        abstract = True

    def delete(self):
        if self.can_delete:
            return super(DefaultDocument, self).delete()
        logger.info(
            "Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}".format(
                self.name
            )
        )


class ProposalApplicantDetails(models.Model):
    first_name = models.CharField(max_length=24, blank=True, default="")

    class Meta:
        app_label = "parkpasses"


class ProposalType(models.Model):
    # class ProposalType(RevisionedMixin):
    code = models.CharField(max_length=30, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        # return 'id: {} code: {}'.format(self.id, self.code)
        return self.description

    class Meta:
        app_label = "parkpasses"


class Proposal(DirtyFieldsMixin, models.Model):
    APPLICANT_TYPE_ORGANISATION = "ORG"
    APPLICANT_TYPE_INDIVIDUAL = "IND"
    APPLICANT_TYPE_PROXY = "PRX"
    APPLICANT_TYPE_SUBMITTER = "SUB"

    PROCESSING_STATUS_DRAFT = "draft"
    PROCESSING_STATUS_AMENDMENT_REQUIRED = "amendment_required"
    PROCESSING_STATUS_WITH_ASSESSOR = "with_assessor"
    PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS = "with_assessor_conditions"
    PROCESSING_STATUS_WITH_APPROVER = "with_approver"
    PROCESSING_STATUS_WITH_REFERRAL = "with_referral"
    PROCESSING_STATUS_WITH_REFERRAL_CONDITIONS = "with_referral_conditions"
    PROCESSING_STATUS_APPROVED_APPLICATION = "approved_application"
    PROCESSING_STATUS_APPROVED_COMPETITIVE_PROCESS = "approved_competitive_process"
    PROCESSING_STATUS_APPROVED_EDITING_INVOICING = "approved_editing_invoicing"
    PROCESSING_STATUS_APPROVED = "approved"
    PROCESSING_STATUS_DECLINED = "declined"
    PROCESSING_STATUS_DISCARDED = "discarded"
    PROCESSING_STATUS_CHOICES = (
        (PROCESSING_STATUS_DRAFT, "Draft"),
        (PROCESSING_STATUS_WITH_ASSESSOR, "With Assessor"),
        (PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS, "With Assessor (Conditions)"),
        (PROCESSING_STATUS_WITH_APPROVER, "With Approver"),
        (PROCESSING_STATUS_WITH_REFERRAL, "With Referral"),
        (PROCESSING_STATUS_WITH_REFERRAL_CONDITIONS, "With Referral (Conditions)"),
        (PROCESSING_STATUS_APPROVED_APPLICATION, "Approved (Application)"),
        (
            PROCESSING_STATUS_APPROVED_COMPETITIVE_PROCESS,
            "Approved (Competitive Process)",
        ),
        (PROCESSING_STATUS_APPROVED_EDITING_INVOICING, "Approved (Editing Invoicing)"),
        (PROCESSING_STATUS_APPROVED, "Approved"),
        (PROCESSING_STATUS_DECLINED, "Declined"),
        (PROCESSING_STATUS_DISCARDED, "Discarded"),
    )

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = [
        PROCESSING_STATUS_DRAFT,
        PROCESSING_STATUS_AMENDMENT_REQUIRED,
    ]

    # List of statuses from above that allow a customer to view an application (read-only)
    CUSTOMER_VIEWABLE_STATE = [
        PROCESSING_STATUS_WITH_ASSESSOR,
        PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS,
        PROCESSING_STATUS_WITH_REFERRAL,
        PROCESSING_STATUS_WITH_REFERRAL_CONDITIONS,
        PROCESSING_STATUS_WITH_APPROVER,
        PROCESSING_STATUS_APPROVED_APPLICATION,
        PROCESSING_STATUS_APPROVED_COMPETITIVE_PROCESS,
        PROCESSING_STATUS_APPROVED_EDITING_INVOICING,
        PROCESSING_STATUS_APPROVED,
        PROCESSING_STATUS_DECLINED,
    ]

    OFFICER_PROCESSABLE_STATE = [
        PROCESSING_STATUS_WITH_ASSESSOR,
        PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS,
        PROCESSING_STATUS_WITH_REFERRAL,  # <-- Be aware
        PROCESSING_STATUS_WITH_REFERRAL_CONDITIONS,  # <-- Be aware
        PROCESSING_STATUS_WITH_APPROVER,
    ]

    ID_CHECK_STATUS_CHOICES = (
        ("not_checked", "Not Checked"),
        ("awaiting_update", "Awaiting Update"),
        ("updated", "Updated"),
        ("accepted", "Accepted"),
    )

    COMPLIANCE_CHECK_STATUS_CHOICES = (
        ("not_checked", "Not Checked"),
        ("awaiting_returns", "Awaiting Returns"),
        ("completed", "Completed"),
        ("accepted", "Accepted"),
    )

    CHARACTER_CHECK_STATUS_CHOICES = (
        ("not_checked", "Not Checked"),
        ("accepted", "Accepted"),
    )

    REVIEW_STATUS_CHOICES = (
        ("not_reviewed", "Not Reviewed"),
        ("awaiting_amendments", "Awaiting Amendments"),
        ("amended", "Amended"),
        ("accepted", "Accepted"),
    )

    proposal_type = models.ForeignKey(
        ProposalType, blank=True, null=True, on_delete=models.SET_NULL
    )
    proposed_issuance_approval = JSONField(blank=True, null=True)
    ind_applicant = models.IntegerField(null=True, blank=True)  # EmailUserRO
    #org_applicant = models.ForeignKey(
    #    Organisation,
    #    blank=True,
    #    null=True,
    #    related_name="org_applications",
    #    on_delete=models.SET_NULL,
    #)
    proxy_applicant = models.IntegerField(null=True, blank=True)  # EmailUserRO
    lodgement_number = models.CharField(max_length=9, blank=True, default="")
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    lodgement_date = models.DateTimeField(blank=True, null=True)
    submitter = models.IntegerField(null=True)  # EmailUserRO
    assigned_officer = models.IntegerField(null=True)  # EmailUserRO
    assigned_approver = models.IntegerField(null=True)  # EmailUserRO
    approved_by = models.IntegerField(null=True)  # EmailUserRO
    processing_status = models.CharField(
        "Processing Status",
        max_length=30,
        choices=PROCESSING_STATUS_CHOICES,
        default=PROCESSING_STATUS_CHOICES[0][0],
    )
    prev_processing_status = models.CharField(max_length=30, blank=True, null=True)

    #approval = models.ForeignKey(
    #    "parkpasses.Approval", null=True, blank=True, on_delete=models.SET_NULL
    #)
    previous_application = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.SET_NULL
    )
    proposed_decline_status = models.BooleanField(default=False)
    # Special Fields
    title = models.CharField(max_length=255, null=True, blank=True)
    application_type = models.ForeignKey(ApplicationType, on_delete=models.PROTECT)
    approval_level = models.CharField(
        "Activity matrix approval level", max_length=255, null=True, blank=True
    )
    approval_comment = models.TextField(blank=True)
    details_text = models.TextField(blank=True)
    # If the proposal is created as part of migration of approvals
    migrated = models.BooleanField(default=False)
    # Registration of Interest generates a Lease Licence
    generated_proposal = models.ForeignKey(
        "self",
        related_name="originating_proposal",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return str(self.id)

    # Append 'P' to Proposal id to generate Lodgement number. Lodgement number and lodgement sequence are used to generate Reference.
    def save(self, *args, **kwargs):
        super(Proposal, self).save(*args, **kwargs)

        if self.lodgement_number == "":
            new_lodgment_id = "A{0:06d}".format(self.pk)
            self.lodgement_number = new_lodgment_id
            self.save()

    @property
    def can_create_final_approval(self):
        return (
            self.fee_paid
            and self.processing_status == Proposal.PROCESSING_STATUS_AWAITING_PAYMENT
        )

    @property
    def reference(self):
        return "{}-{}".format(self.lodgement_number, self.lodgement_sequence)

    @property
    def reversion_ids(self):
        current_revision_id = Version.objects.get_for_object(self).first().revision_id
        versions = (
            Version.objects.get_for_object(self)
            .select_related("revision__user")
            .filter(
                Q(revision__comment__icontains="status")
                | Q(revision_id=current_revision_id)
            )
        )
        version_ids = [[i.id, i.revision.date_created] for i in versions]
        return [
            dict(
                cur_version_id=version_ids[0][0],
                prev_version_id=version_ids[i + 1][0],
                created=version_ids[i][1],
            )
            for i in range(len(version_ids) - 1)
        ]

    @property
    def applicant(self):
        if self.org_applicant:
            return self.org_applicant.organisation
        elif self.ind_applicant:
            email_user = retrieve_email_user(self.ind_applicant)
        elif self.proxy_applicant:
            email_user = retrieve_email_user(self.proxy_applicant)
        else:
            logger.warning(
                "Applicant for the proposal {} not found".format(self.lodgement_number)
            )
            email_user = retrieve_email_user(self.submitter)

        return email_user

    @property
    def applicant_email(self):
        if (
            self.org_applicant
            and hasattr(self.org_applicant.organisation, "email")
            and self.org_applicant.organisation.email
        ):
            return self.org_applicant.organisation.email
        elif self.ind_applicant:
            email_user = retrieve_email_user(self.ind_applicant)
        elif self.proxy_applicant:
            email_user = retrieve_email_user(self.proxy_applicant)
        else:
            email_user = retrieve_email_user(self.submitter)

        return email_user.email

    @property
    def applicant_name(self):
        if isinstance(self.applicant, Organisation):
            return "{}".format(self.org_applicant.organisation.name)
        else:
            names = " ".join(
                [
                    self.applicant.first_name,
                    self.applicant.last_name,
                ]
            )
            return names if names else ""

    @property
    def applicant_details(self):
        if isinstance(self.applicant, Organisation):
            return "{} \n{}".format(
                self.org_applicant.organisation.name, self.org_applicant.address
            )
        else:
            # return "{} {}\n{}".format(
            return "{} {}".format(
                self.applicant.first_name,
                self.applicant.last_name,
                # self.applicant.addresses.all().first()
            )

    @property
    def applicant_address(self):
        if isinstance(self.applicant, Organisation):
            return self.org_applicant.address
        else:
            return self.applicant.residential_address

    @property
    def applicant_id(self):
        return self.applicant.id

    @property
    def applicant_type(self):
        if self.org_applicant:
            return self.APPLICANT_TYPE_ORGANISATION
        elif self.ind_applicant:
            return self.APPLICANT_TYPE_INDIVIDUAL
        elif self.proxy_applicant:
            return self.APPLICANT_TYPE_PROXY
        else:
            return self.APPLICANT_TYPE_SUBMITTER

    @property
    def applicant_field(self):
        if self.org_applicant:
            return "org_applicant"
        elif self.ind_applicant:
            return "ind_applicant"
        elif self.proxy_applicant:
            return "proxy_applicant"
        else:
            return "submitter"

    def qa_officers(self, name=None):
        if not name:
            return (
                QAOfficerGroup.objects.get(default=True)
                .members.all()
                .values_list("email", flat=True)
            )
        else:
            return (
                QAOfficerGroup.objects.get(name=name)
                .members.all()
                .values_list("email", flat=True)
            )

    @property
    def get_history(self):
        """Return the prev proposal versions"""
        l = []
        p = copy.deepcopy(self)
        while p.previous_application:
            l.append(
                dict(
                    id=p.previous_application.id,
                    modified=p.previous_application.modified_date,
                )
            )
            p = p.previous_application
        return l

    @property
    def is_assigned(self):
        return self.assigned_officer is not None

    @property
    def is_temporary(self):
        # return self.customer_status == 'temp' and self.processing_status == 'temp'
        return self.processing_status == "temp"

    @property
    def can_user_edit(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.processing_status in self.CUSTOMER_EDITABLE_STATE

    @property
    def can_user_view(self):
        """
        :return: True if the application is in one of the approved status.
        """
        return self.processing_status in self.CUSTOMER_VIEWABLE_STATE

    @property
    def is_discardable(self):
        """
        An application can be discarded by a customer if:
        1 - It is a draft
        2- or if the application has been pushed back to the user
        """
        # return self.customer_status == 'draft' or self.processing_status == 'awaiting_applicant_response'
        return (
            self.processing_status == "draft"
            or self.processing_status == "awaiting_applicant_response"
        )

    @property
    def is_deletable(self):
        """
        An application can be deleted only if it is a draft and it hasn't been lodged yet
        :return:
        """
        # return self.customer_status == 'draft' and not self.lodgement_number
        return self.processing_status == "draft" and not self.lodgement_number

    @property
    def latest_referrals(self):
        referrals = self.referrals
        for referral in referrals.all():
            print(referral)
        return referrals.all()[:3]

    @property
    def assessor_assessment(self):
        qs = self.assessment.filter(referral=None)
        return qs[0] if qs else None

    @property
    def referral_assessments(self):
        qs = self.assessment.exclude(referral=None)
        return qs if qs else None

    @property
    def permit(self):
        return self.approval.licence_document._file.url if self.approval else None

    @property
    def allowed_assessors(self):
        group = None
        # TODO: Take application_type into account
        if self.processing_status in [
            Proposal.PROCESSING_STATUS_WITH_APPROVER,
        ]:
            group = self.get_approver_group()
        elif self.processing_status in [
            Proposal.PROCESSING_STATUS_WITH_REFERRAL,
            Proposal.PROCESSING_STATUS_WITH_REFERRAL_CONDITIONS,
            Proposal.PROCESSING_STATUS_WITH_ASSESSOR,
            Proposal.PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS,
        ]:
            group = self.get_assessor_group()
        users = (
            list(
                map(
                    lambda id: retrieve_email_user(id),
                    group.get_system_group_member_ids(),
                )
            )
            if group
            else []
        )
        return users

    @property
    def compliance_assessors(self):
        group = self.get_assessor_group()
        return group.members if group else []

    @property
    def can_officer_process(self):
        """:return: True if the application is in one of the processable status for Assessor role."""
        return (
            True
            if self.processing_status in Proposal.OFFICER_PROCESSABLE_STATE
            else True
        )

    @property
    def amendment_requests(self):
        qs = AmendmentRequest.objects.filter(proposal=self)
        return qs

    # Check if there is an pending amendment request exist for the proposal
    @property
    def pending_amendment_request(self):
        qs = AmendmentRequest.objects.filter(proposal=self, status="requested")
        if qs:
            return True
        return False

    @property
    def is_amendment_proposal(self):
        if self.proposal_type == "amendment":
            return True
        return False

    def get_assessor_group(self):
        # TODO: Take application_type into account
        return SystemGroup.objects.get(name=GROUP_NAME_ASSESSOR)

    def get_approver_group(self):
        # TODO: Take application_type into account
        return SystemGroup.objects.get(name=GROUP_NAME_APPROVER)

    def __check_proposal_filled_out(self):
        if not self.data:
            raise exceptions.ProposalNotComplete()
        missing_fields = []
        required_fields = {}
        for k, v in required_fields.items():
            val = getattr(self, k)
            if not val:
                missing_fields.append(v)
        return missing_fields

    @property
    def assessor_recipients(self):
        logger.info("assessor_recipients")
        recipients = []
        group_ids = self.get_assessor_group().get_system_group_member_ids()
        for id in group_ids:
            logger.info(id)
            recipients.append(EmailUser.objects.get(id=id).email)
        return recipients

    @property
    def approver_recipients(self):
        logger.info("assessor_recipients")
        recipients = []
        group_ids = self.get_approver_group().get_system_group_member_ids()
        for id in group_ids:
            logger.info(id)
            recipients.append(EmailUser.objects.get(id=id).email)
        return recipients

    # Check if the user is member of assessor group for the Proposal
    def is_assessor(self, user):
        return user.id in self.get_assessor_group().get_system_group_member_ids()

    # Check if the user is member of assessor group for the Proposal
    def is_approver(self, user):
        return user.id in self.get_assessor_group().get_system_group_member_ids()

    def can_assess(self, user):
        logger.info("can assess")
        logger.info("user")
        logger.info(type(user))
        logger.info(user)
        logger.info(user.id)
        if self.processing_status in [
            "on_hold",
            "with_qa_officer",
            "with_assessor",
            "with_referral",
            "with_assessor_conditions",
        ]:
            logger.info("self.__assessor_group().get_system_group_member_ids()")
            logger.info(self.get_assessor_group().get_system_group_member_ids())
            return user.id in self.get_assessor_group().get_system_group_member_ids()
        elif self.processing_status == Proposal.PROCESSING_STATUS_WITH_APPROVER:
            return user.id in self.get_approver_group().get_system_group_member_ids()
        else:
            return False

    def can_edit_period(self, user):
        if (
            self.processing_status == "with_assessor"
            or self.processing_status == "with_assessor_conditions"
        ):
            # return self.__assessor_group() in user.proposalassessorgroup_set.all()
            return user.id in self.get_assessor_group().get_system_group_member_ids()
        else:
            return False

    def assessor_comments_view(self, user):

        if (
            self.processing_status == "with_assessor"
            or self.processing_status == "with_referral"
            or self.processing_status == "with_assessor_conditions"
            or self.processing_status == "with_approver"
        ):
            try:
                referral = Referral.objects.get(proposal=self, referral=user)
            except:
                referral = None
            if referral:
                return True
            # elif self.__assessor_group() in user.proposalassessorgroup_set.all():
            elif user.id in self.get_assessor_group().get_system_group_member_ids():
                return True
            # elif self.__approver_group() in user.proposalapprovergroup_set.all():
            elif user.id in self.get_approver_group().get_system_group_member_ids():
                return True
            else:
                return False
        else:
            return False

    def has_assessor_mode(self, user):
        status_without_assessor = [
            "with_approver",
            "approved",
            "waiting_payment",
            "declined",
            "draft",
        ]
        if self.processing_status in status_without_assessor:
            return False
        else:
            if self.assigned_officer:
                if self.assigned_officer == user.id:
                    # return self.__assessor_group() in user.proposalassessorgroup_set.all()
                    return (
                        user.id
                        in self.get_assessor_group().get_system_group_member_ids()
                    )
                else:
                    return False
            else:
                # return self.__assessor_group() in user.proposalassessorgroup_set.all()
                return (
                    user.id in self.get_assessor_group().get_system_group_member_ids()
                )

    def log_user_action(self, action, request):
        return ProposalUserAction.log_action(self, action, request.user.id)

    # From DAS
    def validate_map_files(self, request):
        import geopandas as gpd

        try:
            shp_file_qs = self.map_documents.filter(name__endswith=".shp")
            # TODO : validate shapefile and all the other related filese are present
            if shp_file_qs:
                shp_file_obj = shp_file_qs[0]
                shp = gpd.read_file(shp_file_obj.path)
                shp_transform = shp.to_crs(crs=4326)
                shp_json = shp_transform.to_json()
                import json

                if type(shp_json) == str:
                    self.shapefile_json = json.loads(shp_json)
                else:
                    self.shapefile_json = shp_json
                self.save(version_comment="New Shapefile JSON saved.")
                # else:
                #     raise ValidationError('Please upload a valid shapefile')
            else:
                raise ValidationError("Please upload a valid shapefile")
        except:
            raise ValidationError("Please upload a valid shapefile")

    def make_questions_ready(self, referral=None):
        """
        Create checklist answers
        Assessment instance already exits then skip.
        """
        proposal_assessment, created = ProposalAssessment.objects.get_or_create(
            proposal=self, referral=referral
        )
        if created:
            list_type = (
                SectionChecklist.LIST_TYPE_REFERRAL
                if referral
                else SectionChecklist.LIST_TYPE_ASSESSOR
            )
            section_checklists = SectionChecklist.objects.filter(
                application_type=self.application_type,
                list_type=list_type,
                enabled=True,
            )
            for section_checklist in section_checklists:
                for checklist_question in section_checklist.questions.filter(
                    enabled=True
                ):
                    answer = ProposalAssessmentAnswer.objects.create(
                        proposal_assessment=proposal_assessment,
                        checklist_question=checklist_question,
                    )

    def update(self, request, viewset):
        from parkpasses.components.proposals.utils import save_proponent_data

        with transaction.atomic():
            if self.can_user_edit:
                # Save the data first
                save_proponent_data(self, request, viewset)
                self.save()
            else:
                raise ValidationError("You can't edit this proposal at this moment")

    def send_referral(self, request, referral_email, referral_text):
        with transaction.atomic():
            try:
                referral_email = referral_email.lower()
                if (
                    self.processing_status == Proposal.PROCESSING_STATUS_WITH_ASSESSOR
                    or self.processing_status
                    == Proposal.PROCESSING_STATUS_WITH_REFERRAL
                ):
                    self.processing_status = Proposal.PROCESSING_STATUS_WITH_REFERRAL
                    self.save()

                    # Check if the user is in ledger
                    try:
                        user = EmailUser.objects.get(email__icontains=referral_email)
                    except EmailUser.DoesNotExist:
                        # Validate if it is a deparment user
                        department_user = get_department_user(referral_email)
                        if not department_user:
                            raise ValidationError(
                                "The user you want to send the referral to is not a member of the department"
                            )
                        # Check if the user is in ledger or create

                        user, created = EmailUser.objects.get_or_create(
                            email=department_user["email"].lower()
                        )
                        if created:
                            user.first_name = department_user["given_name"]
                            user.last_name = department_user["surname"]
                            user.save()

                    referral = None
                    try:
                        referral = Referral.objects.get(referral=user.id, proposal=self)
                        raise ValidationError(
                            "A referral has already been sent to this user"
                        )
                    except Referral.DoesNotExist:
                        # Create Referral
                        referral = Referral.objects.create(
                            proposal=self,
                            referral=user.id,
                            sent_by=request.user.id,
                            text=referral_text,
                            assigned_officer=request.user.id,
                        )
                        # Create answers for this referral
                        self.make_questions_ready(referral)

                    # Create a log entry for the proposal
                    self.log_user_action(
                        ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(
                            referral.id,
                            self.lodgement_number,
                            "{}({})".format(user.get_full_name(), user.email),
                        ),
                        request,
                    )
                    # Create a log entry for the organisation
                    if self.applicant:
                        pass
                        # TODO: implement logging to ledger/application???
                        # self.applicant.log_user_action(
                        #    ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(
                        #        referral.id, self.lodgement_number, '{}({})'.format(user.get_full_name(), user.email)
                        #    ), request
                        # )
                    # send email
                    send_referral_email_notification(
                        referral,
                        [
                            user.email,
                        ],
                        request,
                    )
                else:
                    raise exceptions.ProposalReferralCannotBeSent()
            except:
                raise

    def assign_officer(self, request, officer):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not self.can_assess(officer):
                    raise ValidationError(
                        "The selected person is not authorised to be assigned to this proposal"
                    )
                if self.processing_status == "with_approver":
                    if officer.id != self.assigned_approver:
                        self.assigned_approver = officer.id
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(
                            ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(
                                self.id,
                                "{}({})".format(officer.get_full_name(), officer.email),
                            ),
                            request,
                        )
                        # Create a log entry for the organisation
                        # applicant_field=getattr(self, self.applicant_field)
                        # applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(self.id,'{}({})'.format(officer.get_full_name(), officer.email)), request)
                else:
                    if officer.id != self.assigned_officer:
                        self.assigned_officer = officer.id
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(
                            ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(
                                self.id,
                                "{}({})".format(officer.get_full_name(), officer.email),
                            ),
                            request,
                        )
                        # Create a log entry for the organisation
                        # applicant_field=getattr(self, self.applicant_field)
                        # applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(self.id,'{}({})'.format(officer.get_full_name(), officer.email)), request)
            except:
                raise

    def assing_approval_level_document(self, request):
        with transaction.atomic():
            try:
                approval_level_document = request.data["approval_level_document"]
                if approval_level_document != "null":
                    try:
                        document = self.documents.get(
                            input_name=str(approval_level_document)
                        )
                    except ProposalDocument.DoesNotExist:
                        document = self.documents.get_or_create(
                            input_name=str(approval_level_document),
                            name=str(approval_level_document),
                        )[0]
                    document.name = str(approval_level_document)
                    # commenting out below tow lines - we want to retain all past attachments - reversion can use them
                    # if document._file and os.path.isfile(document._file.path):
                    #    os.remove(document._file.path)
                    document._file = approval_level_document
                    document.save()
                    d = ProposalDocument.objects.get(id=document.id)
                    self.approval_level_document = d
                    comment = "Approval Level Document Added: {}".format(document.name)
                else:
                    self.approval_level_document = None
                    comment = "Approval Level Document Deleted: {}".format(
                        request.data["approval_level_document_name"]
                    )
                # self.save()
                self.save(
                    version_comment=comment
                )  # to allow revision to be added to reversion history
                self.log_user_action(
                    ProposalUserAction.ACTION_APPROVAL_LEVEL_DOCUMENT.format(self.id),
                    request,
                )
                # Create a log entry for the organisation
                applicant_field = getattr(self, self.applicant_field)
                applicant_field.log_user_action(
                    ProposalUserAction.ACTION_APPROVAL_LEVEL_DOCUMENT.format(self.id),
                    request,
                )
                return self
            except:
                raise

    def unassign(self, request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status == "with_approver":
                    if self.assigned_approver:
                        self.assigned_approver = None
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(
                            ProposalUserAction.ACTION_UNASSIGN_APPROVER.format(self.id),
                            request,
                        )
                        # Create a log entry for the organisation
                        # applicant_field=getattr(self, self.applicant_field)
                        # applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_APPROVER.format(self.id),request)
                else:
                    if self.assigned_officer:
                        self.assigned_officer = None
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(
                            ProposalUserAction.ACTION_UNASSIGN_ASSESSOR.format(self.id),
                            request,
                        )
                        # Create a log entry for the organisation
                        # applicant_field=getattr(self, self.applicant_field)
                        # applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_ASSESSOR.format(self.id),request)
            except:
                raise

    def add_default_requirements(self):
        # Add default standard requirements to Proposal
        due_date = None
        default_requirements = ProposalStandardRequirement.objects.filter(
            application_type=self.application_type, default=True, obsolete=False
        )
        if default_requirements:
            for req in default_requirements:
                r, created = ProposalRequirement.objects.get_or_create(
                    proposal=self, standard_requirement=req, due_date=due_date
                )

    def move_to_status(self, request, status, approver_comment):
        if not self.can_assess(request.user):
            raise exceptions.ProposalNotAuthorized()
        if status in ["with_assessor", "with_assessor_conditions", "with_approver"]:
            if self.processing_status == "with_referral" or self.can_user_edit:
                raise ValidationError(
                    "You cannot change the current status at this time"
                )
            if self.processing_status != status:
                if self.processing_status == "with_approver":
                    self.approver_comment = ""
                    if approver_comment:
                        self.approver_comment = approver_comment
                        self.save()
                        send_proposal_approver_sendback_email_notification(
                            request, self
                        )
                self.processing_status = status
                self.save()
                if status == "with_assessor_conditions":
                    self.add_default_requirements()

                # Create a log entry for the proposal
                if self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR:
                    self.log_user_action(
                        ProposalUserAction.ACTION_BACK_TO_PROCESSING.format(self.id),
                        request,
                    )
                elif (
                    self.processing_status
                    == self.PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS
                ):
                    self.log_user_action(
                        ProposalUserAction.ACTION_ENTER_REQUIREMENTS.format(self.id),
                        request,
                    )
        else:
            raise ValidationError("The provided status cannot be found.")

    def reissue_approval(self, request, status):
        if not self.processing_status == "approved":
            raise ValidationError("You cannot change the current status at this time")
        elif self.approval and self.approval.can_reissue:
            if (
                self.get_approver_group()
                in request.user.proposalapprovergroup_set.all()
            ):
                self.processing_status = status
                # self.save()
                self.save(
                    version_comment="Reissue Approval: {}".format(
                        self.approval.lodgement_number
                    )
                )
                # Create a log entry for the proposal
                self.log_user_action(
                    ProposalUserAction.ACTION_REISSUE_APPROVAL.format(self.id), request
                )
            else:
                raise ValidationError("Cannot reissue Approval. User not permitted.")
        else:
            raise ValidationError("Cannot reissue Approval")

    def proposed_decline(self, request, details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != "with_assessor":
                    raise ValidationError(
                        "You cannot propose to decline if it is not with assessor"
                    )

                reason = details.get("reason")
                ProposalDeclinedDetails.objects.update_or_create(
                    proposal=self,
                    defaults={
                        "officer": request.user.id,
                        "reason": reason,
                        "cc_email": details.get("cc_email", None),
                    },
                )
                self.proposed_decline_status = True
                approver_comment = ""
                self.move_to_status(request, "with_approver", approver_comment)
                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_PROPOSED_DECLINE.format(self.id), request
                )
                # Log entry for organisation
                # TODO: ledger must create EmailUser logs
                # applicant_field=getattr(self, self.applicant_field)
                # applicant_field.log_user_action(ProposalUserAction.ACTION_PROPOSED_DECLINE.format(self.id),request)

                send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def final_decline(self, request, details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != "with_approver":
                    raise ValidationError(
                        "You cannot decline if it is not with approver"
                    )

                (
                    proposal_decline,
                    success,
                ) = ProposalDeclinedDetails.objects.update_or_create(
                    proposal=self,
                    defaults={
                        "officer": request.user.id,
                        "reason": details.get("reason"),
                        "cc_email": details.get("cc_email", None),
                    },
                )
                self.proposed_decline_status = True
                self.processing_status = "declined"
                # self.customer_status = 'declined'
                self.save()
                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_DECLINE.format(self.id), request
                )
                # Log entry for organisation
                # TODO: ledger must create EmailUser logs
                # applicant_field=getattr(self, self.applicant_field)
                # applicant_field.log_user_action(ProposalUserAction.ACTION_DECLINE.format(self.id),request)
                send_proposal_decline_email_notification(
                    self, request, proposal_decline
                )
            except:
                raise

    def on_hold(self, request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (
                    self.processing_status == "with_assessor"
                    or self.processing_status == "with_referral"
                ):
                    raise ValidationError(
                        "You cannot put on hold if it is not with assessor or with referral"
                    )

                self.prev_processing_status = self.processing_status
                self.processing_status = self.PROCESSING_STATUS_ONHOLD
                self.save()
                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_PUT_ONHOLD.format(self.id), request
                )
                # Log entry for organisation
                applicant_field = getattr(self, self.applicant_field)
                applicant_field.log_user_action(
                    ProposalUserAction.ACTION_PUT_ONHOLD.format(self.id), request
                )

                # send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def on_hold_remove(self, request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != "on_hold":
                    raise ValidationError(
                        "You cannot remove on hold if it is not currently on hold"
                    )

                self.processing_status = self.prev_processing_status
                self.prev_processing_status = self.PROCESSING_STATUS_ONHOLD
                self.save()
                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_REMOVE_ONHOLD.format(self.id), request
                )
                # Log entry for organisation
                applicant_field = getattr(self, self.applicant_field)
                applicant_field.log_user_action(
                    ProposalUserAction.ACTION_REMOVE_ONHOLD.format(self.id), request
                )

                # send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def with_qaofficer(self, request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (
                    self.processing_status == "with_assessor"
                    or self.processing_status == "with_referral"
                ):
                    raise ValidationError(
                        "You cannot send to QA Officer if it is not with assessor or with referral"
                    )

                self.prev_processing_status = self.processing_status
                self.processing_status = self.PROCESSING_STATUS_WITH_QA_OFFICER
                self.qaofficer_referral = True
                if self.qaofficer_referrals.exists():
                    qaofficer_referral = self.qaofficer_referrals.first()
                    qaofficer_referral.sent_by = request.user
                    qaofficer_referral.processing_status = "with_qaofficer"
                else:
                    qaofficer_referral = self.qaofficer_referrals.create(
                        sent_by=request.user
                    )

                qaofficer_referral.save()
                self.save()

                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_WITH_QA_OFFICER.format(self.id), request
                )
                # Log entry for organisation
                applicant_field = getattr(self, self.applicant_field)
                applicant_field.log_user_action(
                    ProposalUserAction.ACTION_WITH_QA_OFFICER.format(self.id), request
                )

                # send_approver_decline_email_notification(reason, request, self)
                recipients = self.qa_officers()
                send_qaofficer_email_notification(self, recipients, request)

            except:
                raise

    def with_qaofficer_completed(self, request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != "with_qa_officer":
                    raise ValidationError(
                        "You cannot Complete QA Officer Assessment if processing status not currently With Assessor"
                    )

                self.processing_status = self.prev_processing_status
                self.prev_processing_status = self.PROCESSING_STATUS_WITH_QA_OFFICER

                qaofficer_referral = self.qaofficer_referrals.first()
                qaofficer_referral.qaofficer = request.user
                qaofficer_referral.qaofficer_group = QAOfficerGroup.objects.get(
                    default=True
                )
                qaofficer_referral.qaofficer_text = request.data["text"]
                qaofficer_referral.processing_status = "completed"

                qaofficer_referral.save()
                self.assigned_officer = None
                self.save()

                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_QA_OFFICER_COMPLETED.format(self.id),
                    request,
                )
                # Log entry for organisation
                applicant_field = getattr(self, self.applicant_field)
                applicant_field.log_user_action(
                    ProposalUserAction.ACTION_QA_OFFICER_COMPLETED.format(self.id),
                    request,
                )

                # send_approver_decline_email_notification(reason, request, self)
                recipients = self.qa_officers()
                send_qaofficer_complete_email_notification(self, recipients, request)
            except:
                raise

    def proposed_approval(self, request, details):
        with transaction.atomic():
            try:
                print(details)
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (
                    (
                        self.application_type.name
                        == APPLICATION_TYPE_REGISTRATION_OF_INTEREST
                        and self.processing_status
                        == Proposal.PROCESSING_STATUS_WITH_ASSESSOR
                    )
                    or (
                        self.application_type.name == APPLICATION_TYPE_LEASE_LICENCE
                        and self.processing_status
                        == Proposal.PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS
                    )
                ):
                    raise ValidationError("You cannot propose for approval")
                self.proposed_issuance_approval = {
                    "details": details.get("details"),
                    "cc_email": details.get("cc_email"),
                    "decision": details.get("decision"),
                }
                self.proposed_decline_status = False
                approver_comment = ""
                self.move_to_status(
                    request, Proposal.PROCESSING_STATUS_WITH_APPROVER, approver_comment
                )
                self.assigned_officer = None
                self.save()
                # Log proposal action
                self.log_user_action(
                    ProposalUserAction.ACTION_PROPOSED_APPROVAL.format(self.id), request
                )
                # Log entry for organisation
                applicant_field = getattr(self, self.applicant_field)
                # applicant_field.log_user_action(ProposalUserAction.ACTION_PROPOSED_APPROVAL.format(self.id),request)

                send_approver_approve_email_notification(request, self)
            except Exception as e:
                logger.error(e)
                raise e

    def preview_approval(self, request, details):
        from parkpasses.components.approvals.models import PreviewTempApproval

        with transaction.atomic():
            try:
                # if self.processing_status != 'with_assessor_conditions' or self.processing_status != 'with_approver':
                if not (
                    self.processing_status == "with_assessor_conditions"
                    or self.processing_status == "with_approver"
                ):
                    raise ValidationError(
                        "Licence preview only available when processing status is with_approver. Current status {}".format(
                            self.processing_status
                        )
                    )
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                # if not self.applicant.organisation.postal_address:
                if not self.applicant_address:
                    raise ValidationError(
                        "The applicant needs to have set their postal address before approving this proposal."
                    )

                lodgement_number = (
                    self.previous_application.approval.lodgement_number
                    if self.proposal_type in ["renewal", "amendment"]
                    else None
                )  # renewals/amendments keep same licence number
                preview_approval = PreviewTempApproval.objects.create(
                    current_proposal=self,
                    issue_date=timezone.now(),
                    expiry_date=datetime.datetime.strptime(
                        details.get("due_date"), "%d/%m/%Y"
                    ).date(),
                    start_date=datetime.datetime.strptime(
                        details.get("start_date"), "%d/%m/%Y"
                    ).date(),
                    submitter=self.submitter,
                    org_applicant=self.org_applicant,
                    proxy_applicant=self.proxy_applicant,
                    lodgement_number=lodgement_number,
                )

                # Generate the preview document - get the value of the BytesIO buffer
                licence_buffer = preview_approval.generate_doc(
                    request.user, preview=True
                )

                # clean temp preview licence object
                transaction.set_rollback(True)

                return licence_buffer
            except:
                raise

    def final_approval(self, request, details):
        pass

    def generate_compliances(self, approval, request):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        from parkpasses.components.compliances.models import (
            Compliance,
            ComplianceUserAction,
        )

        # For amendment type of Proposal, check for copied requirements from previous proposal
        if self.proposal_type == "amendment":
            try:
                for r in self.requirements.filter(copied_from__isnull=False):
                    cs = []
                    cs = Compliance.objects.filter(
                        requirement=r.copied_from,
                        proposal=self.previous_application,
                        processing_status="due",
                    )
                    if cs:
                        if r.is_deleted == True:
                            for c in cs:
                                c.processing_status = "discarded"
                                # c.customer_status = 'discarded'
                                c.reminder_sent = True
                                c.post_reminder_sent = True
                                c.save()
                        if r.is_deleted == False:
                            for c in cs:
                                c.proposal = self
                                c.approval = approval
                                c.requirement = r
                                c.save()
            except:
                raise
        # requirement_set= self.requirements.filter(copied_from__isnull=True).exclude(is_deleted=True)
        requirement_set = self.requirements.all().exclude(is_deleted=True)

        # for req in self.requirements.all():
        for req in requirement_set:
            try:
                if req.due_date and req.due_date >= today:
                    current_date = req.due_date
                    # create a first Compliance
                    try:
                        compliance = Compliance.objects.get(
                            requirement=req, due_date=current_date
                        )
                    except Compliance.DoesNotExist:
                        compliance = Compliance.objects.create(
                            proposal=self,
                            due_date=current_date,
                            processing_status="future",
                            approval=approval,
                            requirement=req,
                        )
                        compliance.log_user_action(
                            ComplianceUserAction.ACTION_CREATE.format(compliance.id),
                            request,
                        )
                    if req.recurrence:
                        while current_date < approval.expiry_date:
                            for x in range(req.recurrence_schedule):
                                # Weekly
                                if req.recurrence_pattern == 1:
                                    current_date += timedelta(weeks=1)
                                # Monthly
                                elif req.recurrence_pattern == 2:
                                    current_date += timedelta(weeks=4)
                                    pass
                                # Yearly
                                elif req.recurrence_pattern == 3:
                                    current_date += timedelta(days=365)
                            # Create the compliance
                            if current_date <= approval.expiry_date:
                                try:
                                    compliance = Compliance.objects.get(
                                        requirement=req, due_date=current_date
                                    )
                                except Compliance.DoesNotExist:
                                    compliance = Compliance.objects.create(
                                        proposal=self,
                                        due_date=current_date,
                                        processing_status="future",
                                        approval=approval,
                                        requirement=req,
                                    )
                                    compliance.log_user_action(
                                        ComplianceUserAction.ACTION_CREATE.format(
                                            compliance.id
                                        ),
                                        request,
                                    )
            except:
                raise

    def renew_approval(self, request):
        pass

    def amend_approval(self, request):
        pass


class ProposalLogDocument(Document):
    log_entry = models.ForeignKey(
        "ProposalLogEntry", related_name="documents", on_delete=models.CASCADE
    )
    _file = models.FileField(
        #upload_to=update_proposal_comms_log_filename, max_length=512
    )

    class Meta:
        app_label = "parkpasses"


class ProposalLogEntry(CommunicationsLogEntry):
    proposal = models.ForeignKey(
        Proposal, related_name="comms_logs", on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} - {}".format(self.reference, self.subject)

    class Meta:
        app_label = "parkpasses"

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.proposal.reference
        super(ProposalLogEntry, self).save(**kwargs)


class ProposalRequest(models.Model):
    proposal = models.ForeignKey(
        Proposal, related_name="proposalrequest_set", on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    # fficer = models.ForeignKey(EmailUser, null=True, on_delete=models.SET_NULL)
    officer = models.IntegerField()  # EmailUserRO

    def __str__(self):
        return "{} - {}".format(self.subject, self.text)

    class Meta:
        app_label = "parkpasses"


class AmendmentReason(models.Model):
    reason = models.CharField("Reason", max_length=125)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Application Amendment Reason"  # display name in Admin
        verbose_name_plural = "Application Amendment Reasons"

    def __str__(self):
        return self.reason


class AmendmentRequest(ProposalRequest):
    STATUS_CHOICES = (("requested", "Requested"), ("amended", "Amended"))

    status = models.CharField(
        "Status", max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    # reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])
    reason = models.ForeignKey(
        AmendmentReason, blank=True, null=True, on_delete=models.SET_NULL
    )
    # reason = models.ForeignKey(AmendmentReason)

    class Meta:
        app_label = "parkpasses"

    def generate_amendment(self, request):
        with transaction.atomic():
            try:
                if not self.proposal.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.status == "requested":
                    proposal = self.proposal
                    if proposal.processing_status != "draft":
                        proposal.processing_status = "draft"
                        proposal.customer_status = "draft"
                        proposal.save()
                        proposal.documents.all().update(can_hide=True)
                        proposal.required_documents.all().update(can_hide=True)
                    # Create a log entry for the proposal
                    proposal.log_user_action(
                        ProposalUserAction.ACTION_ID_REQUEST_AMENDMENTS, request
                    )
                    # Create a log entry for the organisation
                    applicant_field = getattr(proposal, proposal.applicant_field)
                    applicant_field.log_user_action(
                        ProposalUserAction.ACTION_ID_REQUEST_AMENDMENTS, request
                    )

                    # send email

                    send_amendment_email_notification(self, request, proposal)

                self.save()
            except:
                raise


class Assessment(ProposalRequest):
    STATUS_CHOICES = (
        ("awaiting_assessment", "Awaiting Assessment"),
        ("assessed", "Assessed"),
        ("assessment_expired", "Assessment Period Expired"),
    )
    # assigned_assessor = models.ForeignKey(EmailUser, blank=True, null=True, on_delete=models.SET_NULL)
    assigned_assessor = models.IntegerField()  # EmailUserRO
    status = models.CharField(
        "Status", max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    date_last_reminded = models.DateField(null=True, blank=True)
    # requirements = models.ManyToManyField('Requirement', through='AssessmentRequirement')
    comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)

    class Meta:
        app_label = "parkpasses"


class ProposalDeclinedDetails(models.Model):
    # proposal = models.OneToOneField(Proposal, related_name='declined_details')
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    # officer = models.ForeignKey(EmailUser, null=False, on_delete=models.CASCADE)
    officer = models.IntegerField()  # EmailUserRO
    reason = models.TextField(blank=True)
    cc_email = models.TextField(null=True)

    class Meta:
        app_label = "parkpasses"


# class ProposalStandardRequirement(models.Model):
class ProposalStandardRequirement(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    obsolete = models.BooleanField(default=False)
    application_type = models.ForeignKey(
        ApplicationType, null=True, blank=True, on_delete=models.SET_NULL
    )
    participant_number_required = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    # require_due_date = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Application Standard Requirement"
        verbose_name_plural = "Application Standard Requirements"


class ProposalUserAction(UserAction):

    class Meta:
        app_label = "parkpasses"
        ordering = ("-when",)

    @classmethod
    def log_action(cls, proposal, action, user):
        return cls.objects.create(proposal=proposal, who=user, what=str(action))

    proposal = models.ForeignKey(
        Proposal, related_name="action_logs", on_delete=models.CASCADE
    )


class ReferralRecipientGroup(models.Model):
    # site = models.OneToOneField(Site, default='1')
    name = models.CharField(max_length=30, unique=True)
    # members = models.ManyToManyField(EmailUser)
    members = ArrayField(models.IntegerField(), blank=True)  # EmailUserRO

    def __str__(self):
        # return 'Referral Recipient Group'
        return self.name

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        # all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    @property
    def members_list(self):
        return list(self.members.all().values_list("email", flat=True))

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Referral group"
        verbose_name_plural = "Referral groups"


class Referral(RevisionedMixin):
    SENT_CHOICES = ((1, "Sent From Assessor"), (2, "Sent From Referral"))
    PROCESSING_STATUS_WITH_REFERRAL = "with_referral"
    PROCESSING_STATUS_RECALLED = "recalled"
    PROCESSING_STATUS_COMPLETED = "completed"
    PROCESSING_STATUS_CHOICES = (
        (PROCESSING_STATUS_WITH_REFERRAL, "Awaiting"),
        (PROCESSING_STATUS_RECALLED, "Recalled"),
        (PROCESSING_STATUS_COMPLETED, "Completed"),
    )
    lodged_on = models.DateTimeField(auto_now_add=True)
    proposal = models.ForeignKey(
        Proposal, related_name="referrals", on_delete=models.CASCADE
    )
    sent_by = models.IntegerField()  # EmailUserRO
    referral = models.IntegerField()  # EmailUserRO
    linked = models.BooleanField(default=False)
    sent_from = models.SmallIntegerField(
        choices=SENT_CHOICES, default=SENT_CHOICES[0][0]
    )
    processing_status = models.CharField(
        "Processing Status",
        max_length=30,
        choices=PROCESSING_STATUS_CHOICES,
        default=PROCESSING_STATUS_CHOICES[0][0],
    )
    text = models.TextField(blank=True)  # Assessor text
    referral_text = models.TextField(blank=True)
    assigned_officer = models.IntegerField()  # EmailUserRO

    class Meta:
        app_label = "parkpasses"
        ordering = ("-lodged_on",)

    def __str__(self):
        return "Application {} - Referral {}".format(self.proposal.id, self.id)

    # Methods
    @property
    def application_type(self):
        return self.proposal.application_type.name

    @property
    def latest_referrals(self):
        return Referral.objects.filter(sent_by=self.referral, proposal=self.proposal)[
            :2
        ]

    @property
    def referral_assessment(self):
        # qs=self.assessment.filter(referral_assessment=True, referral_group=self.referral_group)
        qs = self.assessment.filter(referral_assessment=True)
        if qs:
            return qs[0]
        else:
            return None

    @property
    def can_be_completed(self):
        return True
        # Referral cannot be completed until second level referral sent by referral has been completed/recalled
        qs = Referral.objects.filter(
            sent_by=self.referral,
            proposal=self.proposal,
            processing_status=Referral.PROCESSING_STATUS_WITH_REFERRAL,
        )
        if qs:
            return False
        else:
            return True

    @property
    def allowed_assessors(self):
        pass

    def can_process(self, user):
        pass

    def assign_officer(self, request, officer):
        with transaction.atomic():
            try:
                if not self.can_process(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not self.can_process(officer):
                    raise ValidationError(
                        "The selected person is not authorised to be assigned to this Referral"
                    )
                if officer != self.assigned_officer:
                    self.assigned_officer = officer
                    self.save()
                    self.proposal.log_user_action(
                        ProposalUserAction.ACTION_REFERRAL_ASSIGN_TO_ASSESSOR.format(
                            self.id,
                            self.proposal.id,
                            "{}({})".format(officer.get_full_name(), officer.email),
                        ),
                        request,
                    )
            except:
                raise

    def unassign(self, request):
        with transaction.atomic():
            try:
                if not self.can_process(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.assigned_officer:
                    self.assigned_officer = None
                    self.save()
                    # Create a log entry for the proposal
                    self.proposal.log_user_action(
                        ProposalUserAction.ACTION_REFERRAL_UNASSIGN_ASSESSOR.format(
                            self.id, self.proposal.id
                        ),
                        request,
                    )
                    # Create a log entry for the organisation
                    applicant_field = getattr(
                        self.proposal, self.proposal.applicant_field
                    )
                    applicant_field = retrieve_email_user(applicant_field)
                    # TODO: implement logging
                    # applicant_field.log_user_action(ProposalUserAction.ACTION_REFERRAL_UNASSIGN_ASSESSOR.format(self.id, self.proposal.id),request)
            except:
                raise

    def recall(self, request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            self.processing_status = Referral.PROCESSING_STATUS_RECALLED
            self.save()
            # TODO Log proposal action
            self.proposal.log_user_action(
                ProposalUserAction.RECALL_REFERRAL.format(self.id, self.proposal.id),
                request,
            )
            # TODO log organisation action
            applicant_field = getattr(self.proposal, self.proposal.applicant_field)
            applicant_field = retrieve_email_user(applicant_field)
            # TODO: implement logging
            # applicant_field.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)

    @property
    def referral_as_email_user(self):
        return retrieve_email_user(self.referral)

    def remind(self, request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            # Create a log entry for the proposal
            # self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            # self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            self.proposal.log_user_action(
                ProposalUserAction.ACTION_REMIND_REFERRAL.format(
                    self.id,
                    self.proposal.id,
                    "{}".format(self.referral_as_email_user.get_full_name()),
                ),
                request,
            )
            # Create a log entry for the organisation
            applicant_field = getattr(self.proposal, self.proposal.applicant_field)
            applicant_field = retrieve_email_user(applicant_field)
            # applicant_field.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)

            # TODO: logging applicant_field
            # applicant_field.log_user_action(
            #     ProposalUserAction.ACTION_REMIND_REFERRAL.format(
            #         self.id, self.proposal.id, '{}'.format(self.referral_as_email_user.get_full_name())
            #         ), request
            #     )

            # send email
            # recipients = self.referral_group.members_list
            # send_referral_email_notification(self,recipients,request,reminder=True)
            send_referral_email_notification(
                self,
                [
                    self.referral_as_email_user.email,
                ],
                request,
                reminder=True,
            )

    def resend(self, request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            self.processing_status = Referral.PROCESSING_STATUS_WITH_REFERRAL
            self.proposal.processing_status = Proposal.PROCESSING_STATUS_WITH_REFERRAL
            self.proposal.save()
            self.sent_from = 1
            self.save()
            # Create a log entry for the proposal
            # self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            # self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            self.proposal.log_user_action(
                ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(
                    self.id,
                    self.proposal.id,
                    "{}".format(self.referral_as_email_user.get_full_name()),
                ),
                request,
            )
            # Create a log entry for the organisation
            # self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            applicant_field = getattr(self.proposal, self.proposal.applicant_field)
            applicant_field = retrieve_email_user(applicant_field)

            # TODO: logging applicant_field
            # applicant_field.log_user_action(
            #     ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(
            #         self.id, self.proposal.id, '{}'.format(self.referral_as_email_user.get_full_name())
            #         ), request
            #     )

            # send email
            # recipients = self.referral_group.members_list
            # send_referral_email_notification(self,recipients,request)
            send_referral_email_notification(
                self,
                [
                    self.referral_as_email_user.email,
                ],
                request,
            )

    def complete(self, request):
        with transaction.atomic():
            try:
                self.processing_status = Referral.PROCESSING_STATUS_COMPLETED
                self.referral = request.user.id
                self.add_referral_document(request)
                self.save()

                # TODO Log proposal action
                # self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
                self.proposal.log_user_action(
                    ProposalUserAction.CONCLUDE_REFERRAL.format(
                        request.user.get_full_name(), self.id, self.proposal.id
                    ),
                    request,
                )

                # TODO log organisation action
                # self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
                applicant_field = getattr(self.proposal, self.proposal.applicant_field)
                applicant_field = retrieve_email_user(applicant_field)

                # TODO: logging applicant_field
                # applicant_field.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)

                send_referral_complete_email_notification(self, request)
            except:
                raise

    def add_referral_document(self, request):
        with transaction.atomic():
            try:
                # if request.data.has_key('referral_document'):
                if "referral_document" in request.data:
                    referral_document = request.data["referral_document"]
                    if referral_document != "null":
                        try:
                            document = self.referral_documents.get(
                                input_name=str(referral_document)
                            )
                        except ReferralDocument.DoesNotExist:
                            document = self.referral_documents.get_or_create(
                                input_name=str(referral_document),
                                name=str(referral_document),
                            )[0]
                        document.name = str(referral_document)
                        # commenting out below tow lines - we want to retain all past attachments - reversion can use them
                        # if document._file and os.path.isfile(document._file.path):
                        #    os.remove(document._file.path)
                        document._file = referral_document
                        document.save()
                        d = ReferralDocument.objects.get(id=document.id)
                        # self.referral_document = d
                        self.document = d
                        comment = "Referral Document Added: {}".format(document.name)
                    else:
                        # self.referral_document = None
                        self.document = None
                        # comment = 'Referral Document Deleted: {}'.format(request.data['referral_document_name'])
                        comment = "Referral Document Deleted"
                    # self.save()
                    self.save(
                        version_comment=comment
                    )  # to allow revision to be added to reversion history
                    self.proposal.log_user_action(
                        ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),
                        request,
                    )
                    # Create a log entry for the organisation
                    applicant_field = getattr(
                        self.proposal, self.proposal.applicant_field
                    )
                    applicant_field.log_user_action(
                        ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),
                        request,
                    )
                return self
            except:
                raise

    def send_referral(self, request, referral_email, referral_text):
        with transaction.atomic():
            try:
                if (
                    self.proposal.processing_status
                    == Proposal.PROCESSING_STATUS_WITH_REFERRAL
                ):
                    if request.user != self.referral:
                        raise exceptions.ReferralNotAuthorized()
                    if self.sent_from != 1:
                        raise exceptions.ReferralCanNotSend()
                    self.proposal.processing_status = (
                        Proposal.PROCESSING_STATUS_WITH_REFERRAL
                    )
                    self.proposal.save()
                    referral = None
                    # Check if the user is in ledger
                    try:
                        user = EmailUser.objects.get(
                            email__icontains=referral_email.lower()
                        )
                    except EmailUser.DoesNotExist:
                        # Validate if it is a deparment user
                        department_user = get_department_user(referral_email)
                        if not department_user:
                            raise ValidationError(
                                "The user you want to send the referral to is not a member of the department"
                            )
                        # Check if the user is in ledger or create

                        user, created = EmailUser.objects.get_or_create(
                            email=department_user["email"].lower()
                        )
                        if created:
                            user.first_name = department_user["given_name"]
                            user.last_name = department_user["surname"]
                            user.save()
                    qs = Referral.objects.filter(sent_by=user, proposal=self.proposal)
                    if qs:
                        raise ValidationError("You cannot send referral to this user")
                    try:
                        Referral.objects.get(referral=user, proposal=self.proposal)
                        raise ValidationError(
                            "A referral has already been sent to this user"
                        )
                    except Referral.DoesNotExist:
                        # Create Referral
                        referral = Referral.objects.create(
                            proposal=self.proposal,
                            referral=user,
                            sent_by=request.user,
                            sent_from=2,
                            text=referral_text,
                        )
                        # try:
                        #     referral_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        # except ProposalAssessment.DoesNotExist:
                        #     referral_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        #     checklist=ChecklistQuestion.objects.filter(list_type='referral_list', obsolete=False)
                        #     for chk in checklist:
                        #         try:
                        #             chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=referral_assessment)
                        #         except ProposalAssessmentAnswer.DoesNotExist:
                        #             chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=referral_assessment)
                    # Create a log entry for the proposal
                    self.proposal.log_user_action(
                        ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(
                            referral.id,
                            self.proposal.id,
                            "{}({})".format(user.get_full_name(), user.email),
                        ),
                        request,
                    )
                    # Create a log entry for the organisation
                    applicant_field = getattr(
                        self.proposal, self.proposal.applicant_field
                    )
                    applicant_field.log_user_action(
                        ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(
                            referral.id,
                            self.proposal.id,
                            "{}({})".format(user.get_full_name(), user.email),
                        ),
                        request,
                    )
                    # send email
                    recipients = self.email_group.members_list
                    send_referral_email_notification(referral, recipients, request)
                else:
                    raise exceptions.ProposalReferralCannotBeSent()
            except:
                raise

    @property
    def title(self):
        return self.proposal.title

    @property
    def applicant(self):
        return self.proposal.applicant

    @property
    def can_be_processed(self):
        return self.processing_status == "with_referral"

    def can_assess_referral(self, user):
        return self.processing_status == "with_referral"


class ProposalRequirement(RevisionedMixin):
    RECURRENCE_PATTERNS = [(1, "Weekly"), (2, "Monthly"), (3, "Yearly")]
    standard_requirement = models.ForeignKey(
        ProposalStandardRequirement, null=True, blank=True, on_delete=models.SET_NULL
    )
    free_requirement = models.TextField(null=True, blank=True)
    standard = models.BooleanField(default=True)
    proposal = models.ForeignKey(
        Proposal, related_name="requirements", on_delete=models.CASCADE
    )
    due_date = models.DateField(null=True, blank=True)
    recurrence = models.BooleanField(default=False)
    recurrence_pattern = models.SmallIntegerField(
        choices=RECURRENCE_PATTERNS, default=1
    )
    recurrence_schedule = models.IntegerField(null=True, blank=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )
    is_deleted = models.BooleanField(default=False)
    copied_for_renewal = models.BooleanField(default=False)
    require_due_date = models.BooleanField(default=False)
    # To determine if requirement has been added by referral and the group of referral who added it
    # Null if added by an assessor
    referral_group = models.ForeignKey(
        ReferralRecipientGroup,
        null=True,
        blank=True,
        related_name="requirement_referral_groups",
        on_delete=models.SET_NULL,
    )
    notification_only = models.BooleanField(default=False)
    req_order = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"
        ordering = ["proposal", "req_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["proposal", "req_order"],
                name="unique requirement order per proposal",
            )
        ]

    def save(self, **kwargs):
        # import ipdb; ipdb.set_trace()
        # set the req_order if saving for the first time
        if not self.id:
            max_req_order = (
                ProposalRequirement.objects.filter(proposal_id=self.proposal_id)
                .aggregate(max_req_order=Max("req_order"))
                .get("max_req_order")
            )
            if not max_req_order:
                self.req_order = 1
            else:
                self.req_order = max_req_order + 1
        super(ProposalRequirement, self).save(**kwargs)

    def swap_obj(self, up):
        increment = -1
        swap_increment = None
        for req in ProposalRequirement.objects.filter(
            proposal_id=self.proposal_id, is_deleted=False
        ).order_by("req_order"):
            increment += 1
            if req.id == self.id:
                break
        if up:
            swap_increment = increment - 1
        else:
            swap_increment = increment + 1

        return ProposalRequirement.objects.filter(
            proposal_id=self.proposal_id, is_deleted=False
        ).order_by("req_order")[swap_increment]

    # def _next_req(self):
    #    increment = -1
    #    for req in ProposalRequirement.objects.filter(proposal_id=self.proposal_id, is_deleted=False).order_by('-req_order'):
    #        increment += 1
    #        if req.id == self.id:
    #            break
    #    return ProposalRequirement.objects.filter(proposal_id=self.proposal_id, is_deleted=False).order_by('req_order')[increment]

    def move_up(self):
        # ignore deleted reqs
        if self.req_order == ProposalRequirement.objects.filter(
            is_deleted=False, proposal_id=self.proposal_id
        ).aggregate(min_req_order=Min("req_order")).get("min_req_order"):
            pass
        else:
            # self.swap(ProposalRequirement.objects.get(proposal=self.proposal, req_order=self.req_order-1))
            self.swap(self.swap_obj(True))

    def move_down(self):
        # ignore deleted reqs
        if self.req_order == ProposalRequirement.objects.filter(
            is_deleted=False, proposal_id=self.proposal_id
        ).aggregate(max_req_order=Max("req_order")).get("max_req_order"):
            pass
        else:
            # self.swap(ProposalRequirement.objects.get(proposal=self.proposal, req_order=self.req_order-1))
            self.swap(self.swap_obj(False))
            # self.swap(self._next_req())

    def swap(self, other):
        new_self_position = other.req_order
        print(self.id)
        print("new_self_position")
        print(new_self_position)
        new_other_position = self.req_order
        print(other.id)
        print("new_other_position")
        print(new_other_position)
        # null out both values to prevent a db constraint error on save()
        self.req_order = None
        self.save()
        other.req_order = None
        other.save()
        # set new positions
        self.req_order = new_self_position
        self.save()
        other.req_order = new_other_position
        other.save()

    @property
    def requirement(self):
        return (
            self.standard_requirement.text if self.standard else self.free_requirement
        )

    def can_referral_edit(self, user):
        if self.proposal.processing_status == "with_referral":
            if self.referral_group:
                group = ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
                # user=request.user
                if group and group[0] in user.referralrecipientgroup_set.all():
                    return True
                else:
                    return False
        return False

    def can_district_assessor_edit(self, user):
        allowed_status = [
            "with_district_assessor",
            "partially_approved",
            "partially_declined",
        ]
        if (
            self.district_proposal
            and self.district_proposal.processing_status == "with_assessor_conditions"
            and self.proposal.processing_status in allowed_status
        ):
            if self.district_proposal.can_process_requirements(user):
                return True
        return False

    def add_documents(self, request):
        with transaction.atomic():
            try:
                # save the files
                data = json.loads(request.data.get("data"))
                if not data.get("update"):
                    documents_qs = self.requirement_documents.filter(
                        input_name="requirement_doc", visible=True
                    )
                    documents_qs.delete()
                for idx in range(data["num_files"]):
                    _file = request.data.get("file-" + str(idx))
                    document = self.requirement_documents.create(
                        _file=_file, name=_file.name
                    )
                    document.input_name = data["input_name"]
                    document.can_delete = True
                    document.save()
                # end save documents
                self.save()
            except:
                raise
        return


def clone_proposal_with_status_reset(original_proposal):
    with transaction.atomic():
        try:
            proposal = Proposal.objects.create(
                application_type=ApplicationType.objects.get(name="lease_licence"),
                ind_applicant=original_proposal.ind_applicant,
                org_applicant=original_proposal.org_applicant,
                previous_application=original_proposal,
                approval=original_proposal.approval,
            )
            # proposal.save(no_revision=True)
            return proposal
        except:
            raise


def duplicate_object(self):
    """
    Duplicate a model instance, making copies of all foreign keys pointing to it.
    There are 3 steps that need to occur in order:

        1.  Enumerate the related child objects and m2m relations, saving in lists/dicts
        2.  Copy the parent object per django docs (doesn't copy relations)
        3a. Copy the child objects, relating to the copied parent object
        3b. Re-create the m2m relations on the copied parent object

    """
    related_objects_to_copy = []
    relations_to_set = {}
    # Iterate through all the fields in the parent object looking for related fields
    for field in self._meta.get_fields():
        if field.name in ["proposal", "approval"]:
            print("Continuing ...")
            pass
        elif field.one_to_many:
            # One to many fields are backward relationships where many child objects are related to the
            # parent (i.e. SelectedPhrases). Enumerate them and save a list so we can copy them after
            # duplicating our parent object.
            print("Found a one-to-many field: {}".format(field.name))

            # 'field' is a ManyToOneRel which is not iterable, we need to get the object attribute itself
            related_object_manager = getattr(self, field.name)
            related_objects = list(related_object_manager.all())
            if related_objects:
                print(" - {len(related_objects)} related objects to copy")
                related_objects_to_copy += related_objects

        elif field.many_to_one:
            # In testing so far, these relationships are preserved when the parent object is copied,
            # so they don't need to be copied separately.
            print("Found a many-to-one field: {}".format(field.name))

        elif field.many_to_many:
            # Many to many fields are relationships where many parent objects can be related to many
            # child objects. Because of this the child objects don't need to be copied when we copy
            # the parent, we just need to re-create the relationship to them on the copied parent.
            print("Found a many-to-many field: {}".format(field.name))
            related_object_manager = getattr(self, field.name)
            relations = list(related_object_manager.all())
            if relations:
                print(" - {} relations to set".format(len(relations)))
                relations_to_set[field.name] = relations

    # Duplicate the parent object
    self.pk = None
    self.lodgement_number = ""
    self.save()
    print("Copied parent object {}".format(str(self)))

    # Copy the one-to-many child objects and relate them to the copied parent
    for related_object in related_objects_to_copy:
        # Iterate through the fields in the related object to find the one that relates to the
        # parent model (I feel like there might be an easier way to get at this).
        for related_object_field in related_object._meta.fields:
            if related_object_field.related_model == self.__class__:
                # If the related_model on this field matches the parent object's class, perform the
                # copy of the child object and set this field to the parent object, creating the
                # new child -> parent relationship.
                related_object.pk = None
                # if related_object_field.name=='approvals':
                #    related_object.lodgement_number = None
                ##if isinstance(related_object, Approval):
                ##    related_object.lodgement_number = ''

                setattr(related_object, related_object_field.name, self)
                print(related_object_field)
                try:
                    related_object.save()
                except Exception as e:
                    logger.warn(e)

                text = str(related_object)
                text = (text[:40] + "..") if len(text) > 40 else text
                print("|- Copied child object {}".format(text))

    # Set the many-to-many relations on the copied parent
    for field_name, relations in relations_to_set.items():
        # Get the field by name and set the relations, creating the new relationships
        field = getattr(self, field_name)
        field.set(relations)
        text_relations = []
        for relation in relations:
            text_relations.append(str(relation))
        print(
            "|- Set {} many-to-many relations on {} {}".format(
                len(relations), field_name, text_relations
            )
        )

    return self


from ckeditor.fields import RichTextField


class HelpPage(models.Model):
    HELP_TEXT_EXTERNAL = 1
    HELP_TEXT_INTERNAL = 2
    HELP_TYPE_CHOICES = (
        (HELP_TEXT_EXTERNAL, "External"),
        (HELP_TEXT_INTERNAL, "Internal"),
    )

    application_type = models.ForeignKey(
        ApplicationType, null=True, on_delete=models.SET_NULL
    )
    content = RichTextField()
    description = models.CharField(max_length=256, blank=True, null=True)
    help_type = models.SmallIntegerField(
        "Help Type", choices=HELP_TYPE_CHOICES, default=HELP_TEXT_EXTERNAL
    )
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    class Meta:
        app_label = "parkpasses"
        unique_together = ("application_type", "help_type", "version")
