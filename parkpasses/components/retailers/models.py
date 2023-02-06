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

from parkpasses.components.retailers.emails import RetailerEmails
from parkpasses.components.retailers.exceptions import (
    MultipleDBCARetailerGroupsExist,
    MultipleRACRetailerGroupsExist,
    NoDBCARetailerGroupExists,
    NoRACRetailerGroupExists,
    RetailerGroupHasNoLedgerOrganisationAttached,
    UnableToRetrieveLedgerOrganisation,
)

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


logger = logging.getLogger(__name__)


class District(models.Model):
    # region = models.IntegerField(verbose_name="Ledger Region", null=False, blank=False)
    # see ledger.payments.cash.models.Region
    name = models.CharField(max_length=200, unique=True)
    archive_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RetailerGroup(models.Model):
    ledger_organisation = models.IntegerField(
        verbose_name="Ledger Organisation", unique=True, null=True, blank=False
    )  # see ledger.accounts.models.Organisation
    district = models.ForeignKey(
        District,
        related_name="retailer_group",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    commission_oracle_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Used to allocate commission for external retailers.\
            IMPORTANT: Leave blank for internal retailer groups.",
    )
    commission_percentage = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        blank=False,
        null=False,
        validators=PERCENTAGE_VALIDATOR,
        default=10,
        help_text="IMPORTANT: Enter 0 for internal retailer groups.",
    )
    active = models.BooleanField(default=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Retailer Group"
        ordering = ["ledger_organisation"]

    def __str__(self):
        return self.organisation["organisation_name"]

    def save(self, *args, **kwargs):
        cache.delete(
            settings.CACHE_KEY_GROUP_IDS.format(self._meta.label_lower, str(self.id))
        )
        cache.delete(
            settings.CACHE_KEY_LEDGER_ORGANISATION.format(self.ledger_organisation)
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
            cache_key = settings.CACHE_KEY_LEDGER_ORGANISATION.format(
                self.ledger_organisation
            )
            organisation = cache.get(cache_key)
            if organisation is None:
                organisation_response = get_organisation(self.ledger_organisation)
                if status.HTTP_200_OK == organisation_response["status"]:
                    organisation = organisation_response["data"]
                    cache.set(cache_key, organisation, settings.CACHE_TIMEOUT_24_HOURS)
                else:
                    error_message = f"CRITICAL: Unable to retrieve organisation {self.ledger_organisation} from ledger."
                    logger.error(error_message)
                    raise UnableToRetrieveLedgerOrganisation(error_message)
            return organisation

        critical_message = (
            f"CRITICAL: Retailer Group: {self.id} has no ledger organisation attached."
        )
        logger.critical(critical_message)
        raise RetailerGroupHasNoLedgerOrganisationAttached(critical_message)

    @classmethod
    def get_dbca_retailer_group(self):
        """Passes have a sold_via field which is always populated. The passes sold from the dbca website
        use the retailer group that is returned by this function.
        """
        dbca_retailer_count = RetailerGroup.objects.filter(
            ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
        ).count()
        if 1 == dbca_retailer_count:
            return RetailerGroup.objects.get(
                ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
            )
        if 1 < dbca_retailer_count:
            critical_message = (
                "CRITICAL: There is more than one retailer group whose ledger_organisation = "
                f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID}'"
            )
            logger.critical(critical_message)
            raise MultipleDBCARetailerGroupsExist(critical_message)
        if 0 == dbca_retailer_count:
            critical_message = (
                "CRITICAL: There is no retailer group whose ledger_organisation = "
                f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID}'"
            )
            logger.critical(critical_message)
            raise NoDBCARetailerGroupExists(critical_message)

    @classmethod
    def check_DBCA_retailer_group(cls, messages, critical_issues):
        if not settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID:
            critical_issues.append(
                "CRITICAL: settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID is not set."
            )
            return
        dbca_retailer_count = cls.objects.filter(
            ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
        ).count()
        if 1 == dbca_retailer_count:
            messages.append(
                (
                    "SUCCESS: One DBCA Retailer Group Exists where ledger_organisation = {}"
                ).format(settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID)
            )
        if 1 < dbca_retailer_count:
            critical_issues.append(
                f"CRITICAL: There is more than one retailer group whose ledger_organisation = "
                f"{settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID}. "
                "(Defined in settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID)"
            )
        if 0 == dbca_retailer_count:
            critical_issues.append(
                "CRITICAL: There is no retailer group whose ledger_organisation = "
                f"{settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID}. "
                "(Defined in settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID)"
            )

    @classmethod
    def get_rac_retailer_group(self):
        rac_retailer_count = RetailerGroup.objects.filter(
            ledger_organisation=settings.RAC_RETAILER_GROUP_ORGANISATION_ID
        ).count()
        if 1 == rac_retailer_count:
            return RetailerGroup.objects.get(
                ledger_organisation=settings.RAC_RETAILER_GROUP_ORGANISATION_ID
            )
        if 1 < rac_retailer_count:
            critical_message = (
                "CRITICAL: There is more than one retailer group whose ledger_organisation = "
                f"'{settings.RAC_RETAILER_GROUP_ORGANISATION_ID}'"
            )
            logger.critical(critical_message)
            raise MultipleRACRetailerGroupsExist(critical_message)
        if 0 == rac_retailer_count:
            critical_message = (
                "CRITICAL: There is no retailer group whose ledger_organisation = "
                f"'{settings.RAC_RETAILER_GROUP_ORGANISATION_ID}'"
            )
            logger.critical(critical_message)
            raise NoRACRetailerGroupExists(critical_message)


class RetailerGroupUser(models.Model):
    """A class to represent the many to many relationship between retailers and email users"""

    retailer_group = models.ForeignKey(
        RetailerGroup, on_delete=models.PROTECT, related_name="retailer_group_users"
    )
    emailuser = models.ForeignKey(
        EmailUser, on_delete=models.PROTECT, blank=True, null=True, db_constraint=False
    )
    active = models.BooleanField(default=True)
    is_admin = models.BooleanField(
        default=False, help_text="Admins can invite other users to their group."
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Retailer Group User"
        unique_together = ("retailer_group", "emailuser")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.emailuser} [{self.retailer_group}]"

    def save(self, *args, **kwargs):
        cache.delete(settings.CACHE_KEY_RETAILER.format(str(self.emailuser.id)))
        cache.delete(settings.CACHE_KEY_RETAILER_ADMIN.format(str(self.emailuser.id)))
        cache.delete(
            settings.CACHE_KEY_GROUP_IDS.format(
                self._meta.label_lower, str(self.retailer_group.id)
            )
        )
        super().save(*args, **kwargs)

    @classmethod
    def update_session(cls, request, user_id):
        from parkpasses.helpers import is_retailer

        if is_retailer(request):
            retailer_group_user = (
                RetailerGroupUser.objects.filter(emailuser=user_id)
                .order_by("-datetime_created")
                .first()
            )
            request.session["retailer"] = {
                "id": retailer_group_user.retailer_group.id,
                "name": retailer_group_user.retailer_group.organisation[
                    "organisation_name"
                ],
            }
        else:
            if "retailer" in request.session.keys():
                del request.session["retailer"]


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
