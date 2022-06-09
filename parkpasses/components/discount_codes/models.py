"""
    This module contains the models required for implimenting discount codes
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class DiscountCodeBatch(models.Model):
    """A class to represent a discount code batch

    When saved, a discount code batch will create a series
    of random, unqiue discount codes with the characteristics
    defined in the batch.
    """

    created_by = models.ForeignKey(EmailUser, on_delete=models.PROTECT)
    number = models.CharField(max_length=10)
    datetime_created = models.DateTimeField()
    datetime_updated = models.DateTimeField()
    datetime_expiry = models.DateTimeField()
    codes_to_generate = models.SmallIntegerField()
    times_each_code_can_be_used = models.SmallIntegerField()
    invalidated = models.BooleanField(default=False)
    discount_amount = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True
    )
    discount_percentage = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        blank=True,
        null=True,
        validators=PERCENTAGE_VALIDATOR,
    )


class DiscountCode(models.Model):
    """A class to represent a discount code

    Discount codes are random and unique.
    If remaining_uses is defined then the code can only
    be used that amount of times, otherwise it can be used
    any number of times.
    """

    discount_code_batch = models.ForeignKey(DiscountCodeBatch, on_delete=models.PROTECT)
    code = models.CharField(max_length=50)
    remaining_uses = models.SmallIntegerField(null=False, blank=False)


class DiscountCodeBatchComment(models.Model):
    """A class to represent a discount code batch comment"""

    CREATE = "C"
    UPDATE = "U"
    INVALIDATE = "I"
    ACTION_CHOICES = [
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (INVALIDATE, "Invalidate"),
    ]
    datetime_created = models.DateTimeField()
    user = models.ForeignKey(EmailUser, on_delete=models.PROTECT)
    action = models.CharField(
        max_length=2,
        choices=ACTION_CHOICES,
        default=CREATE,
    )
    reason = models.TextField()
