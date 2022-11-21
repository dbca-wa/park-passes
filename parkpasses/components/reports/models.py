"""
    This module contains the models for implimenting invoices and montly reports.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

from parkpasses.components.retailers.models import RetailerGroup

upload_protected_files_storage = FileSystemStorage(
    location=settings.PROTECTED_MEDIA_ROOT, base_url="/protected_media"
)


class Report(models.Model):
    """A class to represent a report (contains an invoice and a report pdf)"""

    report_number = models.CharField(max_length=10, null=True, blank=True)
    retailer_group = models.ForeignKey(
        RetailerGroup, related_name="%(class)s_retailer_group", on_delete=models.PROTECT
    )
    report = models.FileField(
        null=True, blank=True, max_length=500, storage=upload_protected_files_storage
    )
    invoice = models.FileField(
        null=True, blank=True, max_length=500, storage=upload_protected_files_storage
    )
    invoice_reference = models.CharField(max_length=36, blank=True, null=True)
    uuid = models.CharField(max_length=36, blank=True, null=True)

    PAID = "P"
    UNPAID = "U"
    PROCESSING_STATUS_CHOICES = [
        (PAID, "Paid"),
        (UNPAID, "Unpaid"),
    ]
    processing_status = models.CharField(
        max_length=2,
        choices=PROCESSING_STATUS_CHOICES,
        null=True,
        blank=True,
        default=UNPAID,
    )
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_number}"

    class Meta:
        app_label = "parkpasses"
        ordering = ["-datetime_created", "retailer_group"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.report_number:
            self.report_number = f"IMR{self.pk:06d}"
            super().save(force_update=True)
