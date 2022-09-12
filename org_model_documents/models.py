"""
    This module allows you to easily add User Actions and Communications
    Log Entries to any model in a project.
"""
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models


class DocumentManager(models.Manager):
    """This manager adds convenience methods for querying documents"""

    def get_for_model(self, model):
        content_type = ContentType.objects.get_for_model(model)
        return self.filter(content_type=content_type)

    def get_for_object_reference(self, model, object_id):
        return self.get_for_model(model).filter(object_id=object_id)

    def get_for_object(self, obj):
        return self.get_for_object_reference(obj.__class__, obj.pk)


def org_model_document_path(instance, filename):
    """Stores the document in a unique folder

    based on the content type and object_id
    """
    if settings.ORG_MODEL_DOCUMENTS_MEDIA_ROOT:
        return (
            f"{settings.ORG_MODEL_DOCUMENTS_MEDIA_ROOT}"
            + f"/org_model_documents/{instance.content_type}/{instance.object_id}/{filename}"
        )
    return (
        f"org_model_documents/{instance.content_type}/{instance.object_id}/{filename}"
    )


class Document(models.Model):
    """A class to represent a document

    Documents can be attached to any model in a project
    """

    objects = DocumentManager()

    object_id = models.CharField(
        max_length=191,
        help_text="Primary key of the model.",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Content type of the model.",
    )

    _file = models.FileField(upload_to=org_model_document_path, null=False, blank=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = (models.Index(fields=["content_type", "object_id"]),)

    def __str__(self):
        return f"id {self.object_id} | content_type {self.content_type} | document {self._file.url}"

    @property
    def path(self):
        if self._file:
            return self._file.path
        else:
            return ""

    @property
    def filename(self):
        return os.path.basename(self.path)
