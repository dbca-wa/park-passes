from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from org_model_documents.models import Document


class BulkCreateDocumentSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        return result


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        list_serializer_class = BulkCreateDocumentSerializer

    def create(self, validated_data):
        instance = Document(**validated_data)

        if isinstance(self._kwargs["data"], dict):
            instance.save()

        return instance
