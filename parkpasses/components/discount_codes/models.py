"""
    This module contains the models required for implimenting discount codes
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from parkpasses.ledger_api_utils import retrieve_email_user

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class DiscountCodeBatch(models.Model):
    """A class to represent a discount code batch

    When saved, a discount code batch will create a series
    of random, unqiue discount codes with the characteristics
    defined in the batch.
    """

    created_by = models.IntegerField(null=False, blank=False)  # EmailUserRO
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

    class Meta:
        """Meta for discount code batch - used here to add a custom constraint

        A discount code batch must specify a discount_amount or a discount_percentage.
        """

        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_discount_amount_or_discount_percentage",
                check=(
                    models.Q(
                        discount_amount__isnull=True, discount_percentage__isnull=False
                    )
                    | models.Q(
                        discount_amount__isnull=False, discount_percentage__isnull=True
                    )
                ),
            )
        ]

    @property
    def created_by(self):
        return retrieve_email_user(self.purchaser)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for i in range(self.codes_to_generate):
            pass
            # code = ""
            # discount_code = DiscountCode.objects.create()


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
    discount_code_batch = models.ForeignKey(DiscountCodeBatch, on_delete=models.PROTECT)
    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    action = models.CharField(
        max_length=2,
        choices=ACTION_CHOICES,
        default=CREATE,
    )
    reason = models.TextField()
