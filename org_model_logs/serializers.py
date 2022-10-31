from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from org_model_logs.models import CommunicationsLogEntry, EntryType, UserAction


class EntryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryType
        fields = "__all__"


class UserActionSerializer(serializers.ModelSerializer):
    # In cases where we want to attach documents to a user action it makes it a lot easier
    # to have the content
    user_action_content_type_id = serializers.SerializerMethodField(
        required=False, allow_null=True
    )

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


class CommunicationsLogEntrySerializer(serializers.ModelSerializer):
    entry_type_display_name = serializers.CharField(source="entry_type.entry_type")

    class Meta:
        model = CommunicationsLogEntry
        fields = "__all__"


class CreateCommunicationsLogEntrySerializer(serializers.ModelSerializer):
    app_label = serializers.CharField(required=False)
    model = serializers.CharField(required=False)

    class Meta:
        model = CommunicationsLogEntry
        fields = "__all__"
        # We populate these in the perform_create method of the viewset
        extra_kwargs = {
            "staff": {"required": False},
            "content_type": {"required": False},
        }
