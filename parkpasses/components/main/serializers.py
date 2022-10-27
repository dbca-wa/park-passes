from django.contrib.contenttypes.models import ContentType
from org_model_documents.models import Document
from org_model_documents.serializers import DocumentSerializer
from rest_framework import serializers

from org_model_logs.serializers import BaseCommunicationsLogEntrySerializer
from org_model_logs.serializers import UserActionSerializer as BaseUserActionSerializer
from parkpasses.ledger_api_utils import retrieve_email_user


class UserActionSerializer(BaseUserActionSerializer):
    who = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def get_who(self, obj):
        if 0 == obj.who:
            return "Anonymous User"
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


class CommunicationsLogEntrySerializer(BaseCommunicationsLogEntrySerializer):
    documents = serializers.SerializerMethodField()

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
