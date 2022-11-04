import os

from rest_framework import serializers

from org_model_documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "content_type",
            "object_id",
            "datetime_created",
            "datetime_updated",
            "_file",
            "file_name",
        ]
        read_only_fields = ["file_name"]

    def get_file_name(self, obj):
        return os.path.basename(obj._file.name)
