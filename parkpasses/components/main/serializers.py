from ledger_api_client.ledger_models import EmailUserRO
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from parkpasses.components.main.models import (
    ApplicationType,
    CommunicationsLogEntry,
    Question,
    RequiredDocument,
)


class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=EmailUser.objects.all(), required=False
    )
    documents = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationsLogEntry
        fields = (
            "id",
            "customer",
            "to",
            "fromm",
            "cc",
            "type",
            "reference",
            "subject" "text",
            "created",
            "staff",
            "proposal" "documents",
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class ApplicationTypeSerializer(serializers.ModelSerializer):
    name_display = serializers.SerializerMethodField()
    confirmation_text = serializers.SerializerMethodField()
    # regions = RegionSerializer(many=True)
    # activity_app_types = ActivitySerializer(many=True)
    # tenure_app_types = TenureSerializer(many=True)

    class Meta:
        model = ApplicationType
        # fields = ('id', 'name', 'activity_app_types', 'tenure_app_types')
        # fields = ('id', 'name', 'tenure_app_types')
        fields = "__all__"
        extra_fields = ["name_display", "confirmation_text"]

    def get_name_display(self, obj):
        return obj.name_display

    def get_confirmation_text(self, obj):
        return obj.confirmation_text


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ("id", "park", "activity", "question")


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "answer_one",
            "answer_two",
            "answer_three",
            "answer_four",
            "correct_answer",
            "correct_answer_value",
        )


class BookingSettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=["%d/%m/%Y"])


class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    override = serializers.BooleanField(default=False)


class EmailUserROSerializerForReferral(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    telephone = serializers.CharField(source="phone_number")
    mobile_phone = serializers.CharField(source="mobile_number")

    class Meta:
        model = EmailUserRO
        fields = (
            "id",
            "name",
            "title",
            "email",
            "telephone",
            "mobile_phone",
        )

    def get_name(self, user):
        return user.get_full_name()
