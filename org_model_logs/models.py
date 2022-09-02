"""
    This module allows you to easily add User Actions and Communications
    Log Entries to any model in a project.
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserActionManager(models.Manager):
    """This manager adds convenience methods for querying User Actions"""

    def log_action(self, content_type, object_id, who, what, why=None):
        return self.model.objects.create(
            content_type=content_type,
            object_id=str(object_id),
            who=who,
            what=what,
            why=why,
        )

    def get_for_model(self, model):
        content_type = ContentType.objects.get(model._meta.model)
        return self.filter(content_type=content_type)

    def get_for_object_reference(self, model, object_id):
        return self.get_for_model(model).filter(object_id=object_id)

    def get_for_object(self, obj, model_db=None):
        return self.get_for_object_reference(obj.__class__, obj.pk)


class UserAction(models.Model):
    """A class to represent a log record of who did what and when.

    User actions can be attached to any model in a project
    """

    objects = UserActionManager()

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
    what = models.TextField(null=False, blank=False)
    why = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{what} ({who} at {when}) {why}".format(
            what=self.what, who=self.who, when=self.when, why=str(self.why or "")
        )

    class Meta:
        indexes = (models.Index(fields=["content_type", "object_id"]),)


class EntryType(models.Model):
    type = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        verbose_name = "Entry Type"
        verbose_name_plural = "Entry Types"
        ordering = ["id"]

    def __str__(self):
        return self.type


class CommunicationsLogEntryManager(models.Manager):
    """This manager adds convenience methods for querying Communication Event Logs."""

    def get_for_model(self, model):
        content_type = ContentType.objects.get(model._meta.model)
        return self.filter(content_type=content_type)

    def get_for_object_reference(self, model, object_id):
        return self.get_for_model(model).filter(object_id=object_id)

    def get_for_object(self, obj, model_db=None):
        return self.get_for_object_reference(obj.__class__, obj.pk)


class CommunicationsLogEntry(models.Model):
    """A class to represent communication log entry.

    User actions can be attached to any model in your project
    """

    objects = CommunicationsLogEntryManager()

    object_id = models.CharField(
        max_length=191,
        help_text="Primary key of the model.",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Content type of the model.",
    )

    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.TextField(blank=True, verbose_name="cc")

    entry_type = models.ForeignKey(EntryType, on_delete=models.PROTECT, default=None)

    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(
        max_length=200, blank=True, verbose_name="Subject / Description"
    )
    text = models.TextField(blank=True)
    customer = models.IntegerField()  # EmailUserRO
    staff = models.IntegerField()  # EmailUserRO

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        indexes = (models.Index(fields=["content_type", "object_id"]),)
        verbose_name = "Communications Log Entry"
        verbose_name_plural = "Communications Log Entries"
