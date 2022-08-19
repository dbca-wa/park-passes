"""
    This module contains the models for implimenting invoices and montly reports.
"""
from django.db import models


class Report(models.Model):
    """A class to represent a report (contains an invoice and a report pdf)"""

    report_number = models.CharField(max_length=10, null=True, blank=True)
    concession_type = models.CharField(unique=True, max_length=50)
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
        return f"{self.concession_type}"

    class Meta:
        app_label = "parkpasses"

    def save(self, *args, **kwargs):
        if (
            not self.pass_number
            or "" == self.pass_number
            or 0 == len(self.pass_number.strip())
        ) and self.pk:
            self.pass_number = f"PP{self.pk:06d}"
        super().save(*args, **kwargs)
