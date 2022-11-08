"""
    This module allows you to easily add User Actions and Communications
    Log Entries to any model in a project.
"""
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.text import slugify


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
    return (
        f"org_model_documents/{slugify(instance.content_type.app_label)}/"
        + f"{slugify(instance.content_type.model)}/{instance.object_id}/{filename}"
    )


upload_protected_files_storage = FileSystemStorage(
    location=settings.ORG_MODEL_DOCUMENTS_MEDIA_ROOT, base_url="/protected_media"
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

    _file = models.FileField(
        storage=upload_protected_files_storage,
        upload_to=org_model_document_path,
        null=False,
        blank=False,
    )
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
