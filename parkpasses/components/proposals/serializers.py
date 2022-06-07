from django.conf import settings
from rest_framework import serializers
from django.db.models import Q
from ledger_api_client.ledger_models import (
    EmailUserRO as EmailUser,
)
from parkpasses.components.main.models import ApplicationType
from parkpasses.components.proposals.models import (
    ProposalType,
    Proposal,
    ProposalUserAction,
    ProposalLogEntry,
)
from parkpasses.components.main.serializers import (
    CommunicationLogEntrySerializer,
    ApplicationTypeSerializer,
)
from parkpasses.components.users.serializers import (
    UserAddressSerializer,
    DocumentSerializer,
)

from parkpasses.helpers import is_assessor
from parkpasses.ledger_api_utils import retrieve_email_user
from rest_framework_gis.serializers import GeoFeatureModelSerializer

# from reversion.models import Version


class ProposalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalType
        fields = (
            "id",
            "code",
            "description",
        )

    def get_activities(self, obj):
        return obj.activities.names()


class EmailUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "title",
            "organisation",
            "fullname",
        )

    def get_fullname(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)


class EmailUserAppViewSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    # identification = DocumentSerializer()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "dob",
            "title",
            "organisation",
            "residential_address",
            #'identification',
            "email",
            "phone_number",
            "mobile_number",
        )


class BaseProposalSerializer(serializers.ModelSerializer):
    readonly = serializers.SerializerMethodField(read_only=True)
    documents_url = serializers.SerializerMethodField()
    proposal_type = ProposalTypeSerializer()
    application_type = ApplicationTypeSerializer()
    # is_qa_officer = serializers.SerializerMethodField()
    applicant = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = (
            "id",
            "application_type",
            "proposal_type",
            "title",
            "processing_status",
            "applicant",
            "submitter",
            "assigned_officer",
            "previous_application",
            "get_history",
            "lodgement_date",
            "supporting_documents",
            "requirements",
            "readonly",
            "can_user_edit",
            "can_user_view",
            "documents_url",
            "reference",
            "lodgement_number",
            "can_officer_process",
            "applicant_details",
            "details_text",
        )
        read_only_fields = ("supporting_documents",)

    def get_applicant(self, obj):
        if isinstance(obj, Organisation):
            return obj.applicant.name
        else:
            return " ".join(
                [
                    obj.applicant.first_name,
                    obj.applicant.last_name,
                ]
            )

    def get_documents_url(self, obj):
        return "/media/{}/proposals/{}/documents/".format(
            settings.MEDIA_APP_DIR, obj.id
        )

    def get_readonly(self, obj):
        return False

    def get_processing_status(self, obj):
        return obj.get_processing_status_display()

    def get_review_status(self, obj):
        return obj.get_review_status_display()

    def get_customer_status(self, obj):
        return obj.get_processing_status_display()

    # def get_is_qa_officer(self,obj):
    #     return True

    def get_allow_full_discount(self, obj):
        return (
            True
            if obj.application_type.name == ApplicationType.TCLASS
            and obj.allow_full_discount
            else False
        )


class ListProposalSerializer(BaseProposalSerializer):
    submitter = serializers.SerializerMethodField(read_only=True)
    applicant_name = serializers.CharField(read_only=True)
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    assigned_officer = serializers.SerializerMethodField(read_only=True)
    allowed_assessors = EmailUserSerializer(many=True)
    accessing_user_can_process = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = (
            "id",
            "application_type",
            "proposal_type",
            "approval_level",
            "title",
            "customer_status",
            "processing_status",
            "review_status",
            "applicant",
            "applicant_name",
            "proxy_applicant",
            "submitter",
            "assigned_officer",
            "previous_application",
            "get_history",
            "lodgement_date",
            "readonly",
            "can_user_edit",
            "can_user_view",
            "reference",
            "lodgement_number",
            "lodgement_sequence",
            "can_officer_process",
            "allowed_assessors",
            "proposal_type",
            "qaofficer_referrals",
            "accessing_user_can_process",
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data' defined are requested from the serializer. We
        # also require the following additional fields for some of the mRender functions
        datatables_always_serialize = (
            "id",
            "application_type",
            "proposal_type",
            "title",
            "customer_status",
            "processing_status",
            "applicant",
            "applicant_name",
            "submitter",
            "assigned_officer",
            "lodgement_date",
            "can_user_edit",
            "can_user_view",
            "reference",
            "lodgement_number",
            "can_officer_process",
            "accessing_user_can_process",
        )

    def get_accessing_user_can_process(self, proposal):
        request = self.context["request"]
        user = request.user
        accessing_user_can_process = False

        if proposal.processing_status in [
            Proposal.PROCESSING_STATUS_WITH_ASSESSOR,
            Proposal.PROCESSING_STATUS_WITH_ASSESSOR_CONDITIONS,
        ]:
            if user.id in proposal.get_assessor_group().get_system_group_member_ids():
                accessing_user_can_process = True
        elif proposal.processing_status in [
            Proposal.PROCESSING_STATUS_WITH_APPROVER,
        ]:
            if user.id in proposal.get_approver_group().get_system_group_member_ids():
                accessing_user_can_process = True
        elif proposal.processing_status in [
            Proposal.PROCESSING_STATUS_WITH_REFERRAL,
            Proposal.PROCESSING_STATUS_WITH_REFERRAL_CONDITIONS,
        ]:
            if proposal.referrals.filter(
                Q(referral=user.id),
                Q(processing_status=Referral.PROCESSING_STATUS_WITH_REFERRAL),
            ):
                accessing_user_can_process = True

        return accessing_user_can_process

    def get_submitter(self, obj):
        if obj.submitter:
            email_user = retrieve_email_user(obj.submitter)
            return EmailUserSerializer(email_user).data
        else:
            return ""

    def get_assigned_officer(self, obj):
        if (
            obj.processing_status == Proposal.PROCESSING_STATUS_WITH_APPROVER
            and obj.assigned_approver
        ):
            email_user = retrieve_email_user(obj.assigned_approver)
            return EmailUserSerializer(email_user).data
        if obj.assigned_officer:
            email_user = retrieve_email_user(obj.assigned_officer)
            return EmailUserSerializer(email_user).data
        return None


class ProposalSerializer(BaseProposalSerializer):
    submitter = serializers.SerializerMethodField(read_only=True)
    processing_status = serializers.SerializerMethodField(read_only=True)

    def get_readonly(self, obj):
        return obj.can_user_view

    def get_submitter(self, obj):
        if obj.submitter:
            email_user = retrieve_email_user(obj.submitter)
            return email_user.get_full_name()
        else:
            return None


class InternalProposalSerializer(BaseProposalSerializer):
    applicant = serializers.CharField(read_only=True)
    processing_status = serializers.SerializerMethodField(read_only=True)
    processing_status_id = serializers.SerializerMethodField()
    review_status = serializers.SerializerMethodField(read_only=True)
    submitter = serializers.SerializerMethodField(read_only=True)
    assessor_mode = serializers.SerializerMethodField()
    can_edit_period = serializers.SerializerMethodField()
    current_assessor = serializers.SerializerMethodField()

    allowed_assessors = EmailUserSerializer(many=True)
    approval_level_document = serializers.SerializerMethodField()

    requirements_completed = serializers.SerializerMethodField()
    applicant_obj = serializers.SerializerMethodField()
    accessing_user_roles = (
        serializers.SerializerMethodField()
    )  # Accessing user's roles for this proposal.
    approval_issue_date = (
        serializers.SerializerMethodField()
    )  # Accessing user's roles for this proposal.

    class Meta:
        model = Proposal
        fields = (
            "id",
            "application_type",
            "approval_level",
            "approval_level_document",
            "title",
            "processing_status",
            "review_status",
            "applicant",
            "applicant_obj",
            "org_applicant",
            "proxy_applicant",
            "submitter",
            "applicant_type",
            "assigned_officer",
            "assigned_approver",
            "previous_application",
            "get_history",
            "lodgement_date",
            "requirements",
            "readonly",
            "can_user_edit",
            "can_user_view",
            "documents_url",
            "assessor_mode",
            "current_assessor",
            "latest_referrals",
            "allowed_assessors",
            "proposed_issuance_approval",
            "proposed_decline_status",
            "proposaldeclineddetails",
            "permit",
            "reference",
            "lodgement_number",
            "lodgement_sequence",
            "can_officer_process",
            "proposal_type",
            "applicant_details",
            "other_details",
            "can_edit_period",
            "assessor_assessment",
            "referral_assessments",
            "requirements_completed",
            "processing_status_id",
            "details_text",
        )
        read_only_fields = ("requirements",)

    def get_accessing_user_roles(self, proposal):
        request = self.context.get("request")
        accessing_user = request.user
        roles = []
        if (
            accessing_user.id
            in proposal.get_assessor_group().get_system_group_member_ids()
        ):
            roles.append("assessor")
        if (
            accessing_user.id
            in proposal.get_approver_group().get_system_group_member_ids()
        ):
            roles.append("approver")
        referral_ids = list(proposal.referrals.values_list("referral", flat=True))
        if accessing_user.id in referral_ids:
            roles.append("referral")
        return roles

    def get_applicant_obj(self, obj):
        try:
            return EmailUserSerializer(obj.applicant).data
        except:
            return OrganisationSerializer(obj.applicant).data

    def get_processing_status_id(self, obj):
        return obj.processing_status

    def get_submitter(self, obj):
        if obj.submitter:
            email_user = retrieve_email_user(obj.submitter)
            return EmailUserSerializer(email_user).data
        else:
            return None

    def get_approval_level_document(self, obj):
        if obj.approval_level_document is not None:
            return [
                obj.approval_level_document.name,
                obj.approval_level_document._file.url,
            ]
        else:
            return obj.approval_level_document

    def get_assessor_mode(self, obj):
        # TODO check if the proposal has been accepted or declined
        request = self.context["request"]
        user = (
            request.user._wrapped if hasattr(request.user, "_wrapped") else request.user
        )
        return {
            "assessor_mode": True,
            "has_assessor_mode": obj.has_assessor_mode(user),
            "assessor_can_assess": obj.can_assess(user),
            "assessor_level": "assessor",
            "assessor_box_view": obj.assessor_comments_view(user),
        }

    def get_can_edit_period(self, obj):
        request = self.context["request"]
        user = (
            request.user._wrapped if hasattr(request.user, "_wrapped") else request.user
        )
        return obj.can_edit_period(user)

    def get_readonly(self, obj):
        return True

    def get_requirements_completed(self, obj):
        return True

    def get_current_assessor(self, obj):
        return {
            "id": self.context["request"].user.id,
            "name": self.context["request"].user.get_full_name(),
            "email": self.context["request"].user.email,
        }

    def get_reversion_ids(self, obj):
        return obj.reversion_ids[:5]

    def get_approval_issue_date(self, obj):
        if obj.approval:
            return obj.approval.issue_date.strftime("%d/%m/%Y")

    # def get_fee_invoice_url(self,obj):
    #     return '/cols/payments/invoice-pdf/{}'.format(obj.fee_invoice_reference) if obj.fee_paid else None



class ProposalUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source="who.get_full_name")

    class Meta:
        model = ProposalUserAction
        fields = "__all__"


class ProposalLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = ProposalLogEntry
        fields = "__all__"
        read_only_fields = ("customer",)

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]
