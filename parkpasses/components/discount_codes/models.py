"""
    This module contains the models required for implimenting discount codes
"""
import uuid

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
    discount_code_batch_number = models.CharField(max_length=10, null=True, blank=True)
    datetime_start = models.DateTimeField(null=False, blank=False)
    datetime_expiry = models.DateTimeField(null=False, blank=False)
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
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta for discount code batch - used here to add a custom constraint

        A discount code batch must specify a discount_amount or a discount_percentage.
        """

        app_label = "parkpasses"
        verbose_name = "Discount Code Batch"
        verbose_name_plural = "Discount Code Batches"
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
    def get_created_by(self):
        return retrieve_email_user(self.created_by)

    @property
    def created_by_name(self):
        email_user = retrieve_email_user(self.created_by)
        return f"{email_user.first_name} {email_user.last_name}"

    def __str__(self):
        return f"{self.discount_code_batch_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        existing_discount_codes = DiscountCode.objects.filter(
            discount_code_batch=self
        ).count()
        if 0 == existing_discount_codes:
            for i in range(self.codes_to_generate):
                code_unique = False
                while not code_unique:
                    code = str(uuid.uuid4())[:8].upper()
                    code_count = DiscountCode.objects.filter(code=code).count()
                    if 0 == code_count:
                        code_unique = True
                DiscountCode.objects.create(
                    discount_code_batch=self,
                    code=code,
                    remaining_uses=self.times_each_code_can_be_used,
                )
        if not self.discount_code_batch_number:
            discount_code_batch_number = f"DC{self.pk:06d}"
            self.discount_code_batch_number = discount_code_batch_number
            super().save(*args, **kwargs)


class DiscountCodeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("discount_code_batch")


class DiscountCode(models.Model):
    """A class to represent a discount code

    Discount codes are random and unique.
    If remaining_uses is defined then the code can only
    be used that amount of times, otherwise it can be used
    any number of times.
    """

    objects = DiscountCodeManager()

    discount_code_batch = models.ForeignKey(
        DiscountCodeBatch, related_name="codes", on_delete=models.PROTECT
    )
    code = models.CharField(max_length=50, unique=True)
    remaining_uses = models.SmallIntegerField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        if self.discount_code_batch.discount_percentage:
            discount = f"{self.discount_code_batch.discount_percentage}% Off"
        else:
            discount = f"${self.discount_code_batch.discount_amount} Off"
        return f"{self.code} ({discount})"


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

    class Meta:
        app_label = "parkpasses"
