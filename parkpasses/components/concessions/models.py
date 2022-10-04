"""
    This module contains the models for implimenting concessions.
"""
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from parkpasses.components.passes.models import Pass

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class Concession(models.Model):
    """A class to represent a concession"""

    concession_type = models.CharField(
        unique=True, max_length=50, null=False, blank=False
    )
    discount_percentage = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        blank=False,
        null=False,
        validators=PERCENTAGE_VALIDATOR,
    )
    display_order = models.SmallIntegerField(unique=True, null=True, blank=False)

    def __str__(self):
        return f"{self.concession_type}"

    class Meta:
        app_label = "parkpasses"

    def discount_as_amount(self, pass_price):
        discount_percentage = self.discount_percentage / 100
        discount_amount = pass_price * discount_percentage
        if Decimal(0.00) >= discount_amount:
            return Decimal(0.00)
        if discount_amount >= pass_price:
            return pass_price
        return discount_amount


class ConcessionUsageManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("park_pass")
            .select_related("concession")
        )


class ConcessionUsage(models.Model):
    """When a concession is used to purchase a pass we created a concession usage
    record to keep track of what concession was used to purchase the pass.

    This is needed as a user may be eligible for concession at one point in time
    and then later on they are no longer eligible. So we can't rely on just the user
    information alone and must store this information explicitly."""

    objects = ConcessionUsageManager()

    concession = models.ForeignKey(
        Concession, related_name="concessions", on_delete=models.PROTECT
    )

    park_pass = models.OneToOneField(
        Pass,
        on_delete=models.PROTECT,
        related_name="concession_usage",
        null=False,
        blank=False,
    )

    concession_card_number = models.CharField(
        max_length=50, null=False, blank=False, default=""
    )

    def __str__(self):
        return (
            self.concession.concession_type
            + "("
            + str(self.concession.discount_percentage)
            + "% Off)"
            + " used to purchase park pass "
            + self.park_pass.pass_number
        )

    class Meta:
        app_label = "parkpasses"
