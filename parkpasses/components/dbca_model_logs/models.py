"""
    This module allows you to easily add User Actions and Communications
    Log Entries to any model in your project.
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models, router

from parkpasses import settings


class ModelLogManager(models.Manager):
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


class UserAction(models.Model):
    """A class to represent a log record of who did what and when.

    User actions can be attached to any model in your project
    """

    objects = ModelLogManager()

    object_id = models.CharField(
        max_length=191,
        help_text="Primary key of the model.",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Content type of the model.",
    )

    who = models.IntegerField()  # EmailUserRO
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what, who=self.who, when=self.when
        )

    class Meta:
        app_label = "parkpasses"
        unique_together = (("content_type", "object_id"),)
        indexes = (models.Index(fields=["content_type", "object_id"]),)


class CommunicationsLogEntry(models.Model):
    """A class to represent communication log entry.

    User actions can be attached to any model in your project
    """

    objects = ModelLogManager()

    object_id = models.CharField(
        max_length=191,
        help_text="Primary key of the model.",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Content type of the model.",
    )

    DEFAULT_TYPE = settings.COMMUNICATIONS_LOG_ENTRY_CHOICES[0][0]

    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.TextField(blank=True, verbose_name="cc")

    type = models.CharField(
        max_length=35,
        choices=settings.COMMUNICATIONS_LOG_ENTRY_CHOICES,
        default=DEFAULT_TYPE,
    )
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(
        max_length=200, blank=True, verbose_name="Subject / Description"
    )
    text = models.TextField(blank=True)
    customer = models.IntegerField()  # EmailUserRO
    staff = models.IntegerField()  # EmailUserRO

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        unique_together = (("content_type", "object_id"),)
        indexes = (models.Index(fields=["content_type", "object_id"]),)
