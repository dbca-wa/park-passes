"""
    This module contains the models for implimenting invoices and montly reports.
"""
from django.db import models

from parkpasses.components.retailers.models import RetailerGroup


class Report(models.Model):
    """A class to represent a report (contains an invoice and a report pdf)"""

    report_number = models.CharField(max_length=10, null=True, blank=True)
    retailer_group = models.ForeignKey(
        RetailerGroup, related_name="%(class)s_retailer_group", on_delete=models.PROTECT
    )
    report = models.FileField(null=True, blank=True)
    invoice = models.FileField(null=True, blank=True)
    PAID = "p"
    UNPAID = "U"
    PROCESSING_STATUS_CHOICES = [
        (PAID, "Paid"),
        (UNPAID, "Unpaid"),
    ]
    processing_status = models.CharField(
        max_length=2, choices=PROCESSING_STATUS_CHOICES, null=True, blank=True
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
