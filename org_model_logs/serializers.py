from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from org_model_documents.models import Document
from org_model_documents.serializers import DocumentSerializer
from org_model_logs.models import UserAction
from parkpasses.ledger_api_utils import retrieve_email_user


class UserActionSerializer(serializers.ModelSerializer):
    # In cases where we want to attach documents to a user action it makes it a lot easier
    # to have the content
    user_action_content_type_id = serializers.SerializerMethodField(
        required=False, allow_null=True
    )
    who = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = UserAction
        fields = [
            "id",
            "user_action_content_type_id",
            "object_id",
            "content_type",
            "who",
            "when",
            "what",
            "why",
            "documents",
        ]
        datatables_always_serialize = [
            "id",
            "who",
            "when",
            "what",
            "documents",
        ]

    def get_user_action_content_type_id(self, obj):
        return ContentType.objects.get_for_model(UserAction).id

    def get_who(self, obj):
        return retrieve_email_user(obj.who).get_full_name()

    def get_documents(self, obj):
        documents = []
        content_type = ContentType.objects.get_for_model(obj)
        if Document.objects.filter(
            content_type=content_type, object_id=obj.id
        ).exists():
            documents = Document.objects.filter(
                content_type=content_type, object_id=obj.id
            )
            documents = DocumentSerializer(documents, many=True).data
        return documents
