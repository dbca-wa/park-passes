from django.conf import settings
from ledger_api_client.ledger_models import Address
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from org_model_logs.models import CommunicationsLogEntry
from rest_framework import serializers

from parkpasses.components.main.models import Document
from parkpasses.helpers import in_dbca_domain, is_parkpasses_admin


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("id", "description", "file", "name", "uploaded_date")


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "line1", "locality", "state", "country", "postcode")


class UserFilterSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = ("id", "last_name", "first_name", "email", "name")

    def get_name(self, obj):
        return obj.get_full_name()


class BasicEmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
            "email",
        )


class UserSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    is_department_user = serializers.SerializerMethodField()
    system_settings = serializers.SerializerMethodField()
    is_parkpasses_admin = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
            "email",
            "residential_address",
            "phone_number",
            "mobile_number",
            "personal_details",
            "address_details",
            "contact_details",
            "full_name",
            "is_department_user",
            "is_staff",
            "system_settings",
            "is_parkpasses_admin",
        )

    def get_personal_details(self, obj):
        return True if obj.last_name and obj.first_name else False

    def get_address_details(self, obj):
        return True if obj.residential_address else False

    def get_contact_details(self, obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.phone_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_is_department_user(self, obj):
        if obj.email:
            request = self.context["request"] if self.context else None
            if request:
                return in_dbca_domain(request)
        return False

    def get_is_parkpasses_admin(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_parkpasses_admin(request)
        return False


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
        )


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "phone_number",
            "mobile_number",
        )

    def validate(self, obj):
        domain = None
        if obj["email"]:
            domain = obj["email"].split("@")[1]
        if domain in settings.DEPT_DOMAINS:
            return obj
        else:
            if not obj.get("phone_number") and not obj.get("mobile_number"):
                raise serializers.ValidationError(
                    "You must provide a mobile/phone number"
                )
        return obj


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
            "log_type",
            "reference",
            "subject" "text",
            "created",
            "staff",
            "emailuser",
            "documents",
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]
