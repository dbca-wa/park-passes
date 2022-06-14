"""
    This module allows you to easily add User Actions and Communications
    Log Entries to any model in a project.
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models, router


class DocumentManager(models.Manager):
    """This manager adds convenience methods for querying User Actions

    and Communication Event Logs.
    """

    def get_for_model(self, model, model_db=None):
        model_db = model_db or router.db_for_write(model)
        content_type = ContentType.objects.get(model._meta.model)
        return self.get_queryset().filter(
            content_type=content_type,
            db=model_db,
        )

    def get_for_object_reference(self, model, object_id, model_db=None):
        return self.get_for_model(model, model_db=model_db).filter(
            object_id=object_id,
        )

    def get_for_object(self, obj, model_db=None):
        return self.get_queryset().get_for_object_reference(
            obj.__class__, obj.pk, model_db=model_db
        )


def org_model_document_path(instance, filename):
    """Stores the document in a unique folder

    based on the content type and object_id
    """
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

    def __str__(self):
        return f"id {self.object_id} | content_type {self.content_type} | document {self.document.url}"

    class Meta:
        unique_together = (("content_type", "object_id"),)
        indexes = (models.Index(fields=["content_type", "object_id"]),)
