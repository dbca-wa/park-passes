"""
    This module contains the models for implimenting retailers.
"""
import json
import logging
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.utils import get_organisation
from rest_framework import status
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager

from parkpasses.components.retailers.emails import RetailerEmails
from parkpasses.components.retailers.exceptions import (
    MultipleDBCARetailerGroupsExist,
    MultipleRACRetailerGroupsExist,
    NoDBCARetailerGroupExists,
    NoRACRetailerGroupExists,
    RetailerGroupHasNoLedgerOrganisationAttached,
)

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


logger = logging.getLogger(__name__)


class RetailerGroup(models.Model):
    ledger_organisation = models.IntegerField(
        verbose_name="Ledger Organisation", unique=True, null=True, blank=False
    )
    name = models.CharField(max_length=150, unique=True, blank=False)
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
        cache.delete(
            settings.CACHE_KEY_GROUP_IDS.format(self._meta.label_lower, str(self.id))
        )
        # If we deactivated a retailer group then all the users in that group need to be kicked out
        for retailer_group_user in self.retailer_group_users.all():
            cache.delete(
                settings.CACHE_KEY_RETAILER.format(
                    str(retailer_group_user.emailuser.id)
                )
            )
            cache.delete(
                settings.CACHE_KEY_RETAILER_ADMIN.format(
                    str(retailer_group_user.emailuser.id)
                )
            )

        super().save(*args, **kwargs)

    def get_user_ids(self):
        cache_key = settings.CACHE_KEY_GROUP_IDS.format(
            self._meta.label_lower, str(self.id)
        )
        user_ids_cache = cache.get(cache_key)
        if user_ids_cache is None:
            user_ids = list(
                RetailerGroupUser.objects.filter(retailer_group=self)
                .values_list("emailuser__id", flat=True)
                .order_by("id")
            )
            cache.set(cache_key, json.dumps(user_ids), settings.CACHE_TIMEOUT_24_HOURS)
        else:
            user_ids = json.loads(user_ids_cache)
        return user_ids

    @property
    def organisation(self):
        if self.ledger_organisation:
            organisation_response = get_organisation(self.ledger_organisation)
            if status.HTTP_200_OK == organisation_response["status"]:
                return organisation_response["data"]
        critical_message = f"CRITICAL: Retailer Group: {self.name} has no ledger organisation attached."
        logger.critical(critical_message)
        raise RetailerGroupHasNoLedgerOrganisationAttached(critical_message)

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
            critical_message = (
                "CRITICAL: There is more than one retailer group whose name = "
                f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA}'"
            )
            logger.critical(critical_message)
            raise MultipleDBCARetailerGroupsExist(critical_message)
        if 0 == dbca_retailer_count:
            critical_message = (
                "CRITICAL: There is no retailer group whose name = "
                f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA}'"
            )
            logger.critical(critical_message)
            raise NoDBCARetailerGroupExists(critical_message)

    @classmethod
    def get_rac_retailer_group(self):
        rac_retailer_count = RetailerGroup.objects.filter(
            name=settings.RAC_RETAILER_GROUP_NAME
        ).count()
        if 1 == rac_retailer_count:
            return RetailerGroup.objects.get(name=settings.RAC_RETAILER_GROUP_NAME)
        if 1 < rac_retailer_count:
            critical_message = (
                "CRITICAL: There is more than one retailer group whose name = "
                f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA}'"
            )
            logger.critical(critical_message)
            raise MultipleRACRetailerGroupsExist(critical_message)
        if 0 == rac_retailer_count:
            critical_message = (
                "CRITICAL: There is no retailer group whose name = "
                f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA}'"
            )
            logger.critical(critical_message)
            raise NoRACRetailerGroupExists(critical_message)


class OrganizationAPIKeyManager(BaseAPIKeyManager):
    def get_usable_keys(self):
        return super().get_usable_keys().filter(retailer_group__active=True)


class RetailerGroupAPIKey(AbstractAPIKey):
    objects = OrganizationAPIKeyManager()
    retailer_group = models.ForeignKey(
        RetailerGroup,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    class Meta(AbstractAPIKey.Meta):
        app_label = "parkpasses"
        verbose_name = "Retailer Group API key"
        verbose_name_plural = "Retailer Group API keys"


class RetailerGroupUser(models.Model):
    """A class to represent the many to many relationship between retailers and email users"""

    retailer_group = models.ForeignKey(
        RetailerGroup, on_delete=models.PROTECT, related_name="retailer_group_users"
    )
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
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.retailer_group} {self.emailuser}"

    def save(self, *args, **kwargs):
        cache.delete(settings.CACHE_KEY_RETAILER.format(str(self.emailuser.id)))
        cache.delete(settings.CACHE_KEY_RETAILER_ADMIN.format(str(self.emailuser.id)))
        cache.delete(
            settings.CACHE_KEY_GROUP_IDS.format(
                self._meta.label_lower, str(self.retailer_group.id)
            )
        )
        super().save(*args, **kwargs)


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
            RetailerEmails.send_retailer_group_user_approved_notification_email(
                self, is_admin
            )
