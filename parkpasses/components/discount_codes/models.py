"""
    This module contains the models required for implimenting discount codes
"""
import logging
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.passes.models import Pass, PassType
from parkpasses.ledger_api_utils import retrieve_email_user

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


logger = logging.getLogger(__name__)


class DiscountCodeBatchManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("discount_codes", "valid_pass_types", "valid_users")
        )


class DiscountCodeBatch(models.Model):
    """A class to represent a discount code batch

    When saved, a discount code batch will create a series
    of random, unqiue discount codes with the characteristics
    defined in the batch.
    """

    objects = DiscountCodeBatchManager()

    created_by = models.IntegerField(null=False, blank=False)  # EmailUserRO
    discount_code_batch_number = models.CharField(max_length=10, null=True, blank=True)
    datetime_start = models.DateTimeField(null=False, blank=False)
    datetime_expiry = models.DateTimeField(null=False, blank=False)
    codes_to_generate = models.SmallIntegerField()
    times_each_code_can_be_used = models.SmallIntegerField(null=True, blank=True)
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
        if existing_discount_codes < self.codes_to_generate:
            difference = self.codes_to_generate - existing_discount_codes
            for i in range(difference):
                code_unique = False
                while not code_unique:
                    code = str(uuid.uuid4())[:8].upper()
                    code_count = DiscountCode.objects.filter(code=code).count()
                    if 0 == code_count:
                        code_unique = True
                DiscountCode.objects.create(
                    discount_code_batch=self,
                    code=code,
                )
        elif existing_discount_codes > self.codes_to_generate:
            difference = existing_discount_codes - self.codes_to_generate
            existing_discount_codes = DiscountCode.objects.filter(
                discount_code_batch=self
            )
            discount_codes = DiscountCode.objects.filter(
                discount_code_batch=self
            ).order_by("?")[:difference]
            for discount_code in discount_codes:
                discount_code.delete()
        if not self.discount_code_batch_number:
            discount_code_batch_number = f"DC{self.pk:06d}"
            self.discount_code_batch_number = discount_code_batch_number
            super().save(force_insert=False)

    def valid_pass_type_ids(self):
        return list(self.valid_pass_types.values_list("pass_type_id", flat=True))

    def valid_user_ids(self):
        return list(self.valid_users.values_list("user", flat=True))


class DiscountCodeBatchValidPassTypeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("pass_type")


class DiscountCodeBatchValidPassType(models.Model):
    objects = DiscountCodeBatchValidPassTypeManager()

    discount_code_batch = models.ForeignKey(
        DiscountCodeBatch,
        related_name="valid_pass_types",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    pass_type = models.ForeignKey(
        PassType,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Valid Pass Type"
        unique_together = (("discount_code_batch", "pass_type"),)

    def __str__(self):
        return (
            f"Pass Type: {self.pass_type.display_name} (id:{self.pass_type.id})"
            f'is valid for Discount Code Batch" {self.discount_code_batch.discount_code_batch_number}'
        )


class DiscountCodeBatchValidUser(models.Model):
    discount_code_batch = models.ForeignKey(
        DiscountCodeBatch,
        related_name="valid_users",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    user = models.IntegerField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Valid User"
        unique_together = (("discount_code_batch", "user"),)

    @property
    def display_name(self):
        email_user = retrieve_email_user(self.user)
        return f"{email_user.first_name} {email_user.last_name} ({email_user.email})"


class DiscountCodeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("discount_code_usages")


class DiscountCode(models.Model):
    """A class to represent a discount code

    Discount codes are random and unique.
    If remaining_uses is defined in the discount code batch then the code can only
    be used that amount of times, otherwise it can be used
    any number of times.
    """

    objects = DiscountCodeManager()

    discount_code_batch = models.ForeignKey(
        DiscountCodeBatch, related_name="discount_codes", on_delete=models.CASCADE
    )
    code = models.CharField(max_length=50, unique=True, null=False, blank=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        if self.discount_code_batch.discount_percentage:
            discount = f"{self.discount_code_batch.discount_percentage}% Off"
        else:
            discount = f"${self.discount_code_batch.discount_amount} Off"
        return f"{self.code} ({discount})"

    @property
    def has_expired(self):
        return self.discount_code_batch.datetime_expiry < timezone.now()

    @property
    def remaining_uses(self):
        times_code_can_be_used = self.discount_code_batch.times_each_code_can_be_used
        if not times_code_can_be_used:
            return settings.UNLIMITED_USES
        current_uses = self.discount_code_usages.count()
        return times_code_can_be_used - current_uses

    @property
    def discount_type(self):
        if self.discount_code_batch.discount_percentage:
            return "percentage"
        return "amount"

    @property
    def discount(self):
        if self.discount_code_batch.discount_percentage:
            return self.discount_code_batch.discount_percentage
        return self.discount_code_batch.discount_amount

    def discount_as_amount(self, pass_price):
        discount_amount = Decimal(0.00)
        if self.discount_code_batch.discount_amount:
            discount_amount = self.discount_code_batch.discount_amount
        else:
            discount_percentage = self.discount_code_batch.discount_percentage / 100
            discount_amount = pass_price * discount_percentage
        if Decimal(0.00) >= discount_amount:
            return Decimal(0.00)
        if discount_amount >= pass_price:
            return pass_price
        return discount_amount

    def is_valid_for_pass_type(self, pass_type_id):
        # If no valid pass types are specified that means the code is valid for all pass types
        if not len(self.discount_code_batch.valid_pass_types.all()):
            return True
        if PassType.objects.filter(id=pass_type_id).exists():
            if int(pass_type_id) in self.discount_code_batch.valid_pass_type_ids():
                return True
        return False

    def is_valid_for_email(self, email):
        """This method can be called before we have a user id in the session as it uses the email they have entered
        on the purchase pass form"""
        # If no users are specified that means the code is valid for all users
        if not len(self.discount_code_batch.valid_users.all()):
            return True

        if EmailUser.objects.filter(email=email).exists():
            email_user = EmailUser.objects.get(email=email)
            if email_user.id in self.discount_code_batch.valid_user_ids():
                return True

        return False

    def is_valid_for_user(self, user_id):
        """This method will be useful once the user has logged in as we can check the user id is valid for the discount_code
        without having to hit the ledger api"""
        # If no users are specified that means the code is valid for all users
        if not len(self.discount_code_batch.valid_users.all()):
            return True

        if user_id in self.discount_code_batch.valid_user_ids():
            return True

        return False

    @classmethod
    def is_valid(self, code, user_id, pass_type_id):
        if not DiscountCode.objects.filter(code=code).exists():
            return False
        discount_code = DiscountCode.objects.get(code=code)
        if discount_code.has_expired:
            return False
        if 1 > discount_code.remaining_uses:
            return False
        if not discount_code.is_valid_for_pass_type(pass_type_id):
            return False
        if not discount_code.is_valid_for_user(user_id):
            return False

        """ To get here the discount code must:
            - Exist
            - Have not expired yet
            - Still have 1 or more remaining uses
            - Be valid for the Pass Type of the purchase
            - Be valid for the specific user that is purchasing the pass
        """
        return True


class DiscountCodeUsage(models.Model):
    """A class to represent a discount code

    Every time a discount code is used a discount code usage record will be created
    to show which park pass the discount code was used for"""

    discount_code = models.ForeignKey(
        DiscountCode,
        related_name="discount_code_usages",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )
    park_pass = models.OneToOneField(
        Pass,
        on_delete=models.PROTECT,
        related_name="discount_code_usage",
        null=False,
        blank=False,
    )

    def __str__(self):
        if self.discount_code.discount_code_batch.discount_amount:
            discount = f"${self.discount_code.discount_code_batch.discount_amount}"
        else:
            discount = (
                f"{self.discount_code.discount_code_batch.discount_percentage}% Off"
            )
        str_value = (
            "Discount Code "
            + self.discount_code.code
            + " ("
            + discount
            + ")"
            + " used to purchase Park Pass "
            + self.park_pass.pass_number
        )
        return str_value

    class Meta:
        app_label = "parkpasses"


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
