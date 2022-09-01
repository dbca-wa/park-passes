from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from org_model_logs.models import UserAction


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
        ]

    def get_user_action_content_type_id(self, obj):
        return ContentType.objects.get_for_model(UserAction).id
