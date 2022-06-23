"""
    This module contains the models for implimenting help messages.
"""
from ckeditor.fields import RichTextField
from django.db import models


class HelpText(models.Model):
    """A class to represent a help text item"""

    label = models.CharField(unique=True, max_length=50, null=False, blank=False)
    content = RichTextField()
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    def __str__(self):
        return f"Help Text Item for {self.label} (Version: {self.version})"

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Help Text"
        verbose_name_plural = "Help Text"
