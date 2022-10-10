"""
    This module contains the models for implimenting retailers.
"""
import json
import logging
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models, transaction
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.retailers.emails import RetailerEmails
from parkpasses.components.retailers.exceptions import (
    MultipleDBCARetailerGroupsExist,
    NoDBCARetailerGroupExists,
)

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


logger = logging.getLogger(__name__)


class RetailerGroup(models.Model):
    NEW_SOUTH_WALES = "NSW"
    VICTORIA = "VIC"
    QUEENSLAND = "QLD"
    WESTERN_AUSTRALIA = "WA"
    SOUTH_AUSTRALIA = "SA"
    TASMANIA = "TAS"
    AUSTRALIAN_CAPITAL_TERRITORY = "ACT"
    NORTHERN_TERRITORY = "NT"

    STATE_CHOICES = [
        (NEW_SOUTH_WALES, "Western Australia"),
        (VICTORIA, "Victoria"),
        (QUEENSLAND, "Queensland"),
        (WESTERN_AUSTRALIA, "Western Australia"),
        (SOUTH_AUSTRALIA, "South Australia"),
        (TASMANIA, "Tasmania"),
        (AUSTRALIAN_CAPITAL_TERRITORY, "Australian Capital Territory"),
        (NORTHERN_TERRITORY, "Western Australia"),
    ]

    name = models.CharField(max_length=150, unique=True, blank=False)
    address_line_1 = models.CharField(max_length=150, null=True, blank=False)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True)
    suburb = models.CharField(max_length=50, null=True, blank=False)
    state = models.CharField(
        max_length=3,
        choices=STATE_CHOICES,
        default=WESTERN_AUSTRALIA,
        null=True,
        blank=False,
    )
    postcode = models.CharField(
        max_length=4,
        validators=[
            MinLengthValidator(4, "Australian postcodes must contain 4 digits")
        ],
        null=True,
        blank=False,
    )
    oracle_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    commission_percentage = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        blank=False,
        null=False,
        validators=PERCENTAGE_VALIDATOR,
        default=10,
    )
    active = models.BooleanField(default=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Retailer Group"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def save(self, *args, **kwargs):
        cache.delete(f"{self._meta.label_lower}.{str(self.id)}")
        cache.delete(f"{self._meta.label_lower}.{str(self.id)}.user_ids")
        super().save(*args, **kwargs)

    def get_user_ids(self):
        user_ids_cache = cache.get(f"{self._meta.label_lower}.{str(self.id)}.user_ids")
        if user_ids_cache is None:
            user_ids = list(
                RetailerGroupUser.objects.filter(retailer_group=self)
                .values_list("emailuser__id", flat=True)
                .order_by("id")
            )
            cache.set(
                f"{self._meta.label_lower}.{str(self.id)}.user_ids",
                json.dumps(user_ids),
                86400,
            )
        else:
            user_ids = json.loads(user_ids_cache)
        return user_ids

    @classmethod
    def get_dbca_retailer_group(self):
        """Passes have a sold_via field which is always populated. The passes sold from the dbca website
        use the retailer group that is returned by this function.
        """
        dbca_retailer_count = RetailerGroup.objects.filter(
            name=settings.PARKPASSES_DEFAULT_SOLD_VIA
        ).count()
        if 1 == dbca_retailer_count:
            return RetailerGroup.objects.get(name=settings.PARKPASSES_DEFAULT_SOLD_VIA)
        if 1 < dbca_retailer_count:
            logger.critical(
                "CRITICAL: There is more than one retailer group whose name contains 'DBCA'"
            )
            raise MultipleDBCARetailerGroupsExist(
                "CRITICAL: There is more than one retailer group whose name contains 'DBCA'"
            )
        if 0 == dbca_retailer_count:
            logger.critical(
                "CRITICAL: There is no retailer group whose name contains 'DBCA'"
            )
            raise NoDBCARetailerGroupExists(
                "CRITICAL: There is no retailer group whose name contains 'DBCA'"
            )


class RetailerGroupUser(models.Model):
    """A class to represent the many to many relationship between retailers and email users"""

    retailer_group = models.ForeignKey(RetailerGroup, on_delete=models.PROTECT)
    emailuser = models.ForeignKey(
        EmailUser, on_delete=models.PROTECT, blank=True, null=True, db_constraint=False
    )
    active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Retailer Group User"
        unique_together = ("retailer_group", "emailuser")

    def __str__(self):
        return f"{self.retailer_group} {self.emailuser}"


class RetailerGroupInviteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("retailer_group")


class RetailerGroupInvite(models.Model):
    user = models.IntegerField(null=True, blank=True)  # EmailUserRO
    email = models.EmailField(null=False, blank=False)
    retailer_group = models.ForeignKey(
        RetailerGroup, on_delete=models.PROTECT, null=False, blank=False
    )
    uuid = models.UUIDField(
        unique=True, null=False, blank=False, default=uuid.uuid4, editable=False
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    NEW = "N"
    SENT = "S"
    USER_LOGGED_IN = "ULI"
    USER_ACCEPTED = "UA"
    DENIED = "D"
    APPROVED = "A"

    STATUS_CHOICES = [
        (NEW, "New"),
        (SENT, "Sent"),
        (USER_LOGGED_IN, "User Logged In"),
        (USER_ACCEPTED, "User Accepted"),
        (DENIED, "Denied"),
        (APPROVED, "Approved"),
    ]

    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=NEW)

    INTERNAL_USER = "I"
    RETAILER_USER = "R"

    INITIATED_BY_CHOICES = [
        (INTERNAL_USER, "Internal User"),
        (RETAILER_USER, "Retailer user"),
    ]

    initiated_by = models.CharField(
        max_length=3, choices=INITIATED_BY_CHOICES, default=INTERNAL_USER
    )

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Retailer Group Invite"
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.email} invited to join {self.retailer_group} [{self.get_status_display()}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.debug("self.status -> " + str(self.status))
        if RetailerGroupInvite.NEW == self.status:
            with transaction.atomic():
                message = (
                    RetailerEmails.send_retailer_group_user_invite_notification_email(
                        self
                    )
                )
                if message:
                    self.status = RetailerGroupInvite.SENT
                    super().save(update_fields=["status"])
        if RetailerGroupInvite.USER_ACCEPTED == self.status:
            message = (
                RetailerEmails.send_retailer_group_user_accepted_notification_email(
                    self
                )
            )
        if RetailerGroupInvite.DENIED == self.status:
            RetailerEmails.send_retailer_group_user_denied_notification_email(self)
        if RetailerGroupInvite.APPROVED == self.status:
            is_admin = (
                RetailerGroupUser.objects.values_list("is_admin", flat=True)
                .filter(retailer_group=self.retailer_group, emailuser=self.user)
                .first()
            )
            logger.debug("is_admin = " + str(is_admin))
            RetailerEmails.send_retailer_group_user_approved_notification_email(
                self, is_admin
            )
