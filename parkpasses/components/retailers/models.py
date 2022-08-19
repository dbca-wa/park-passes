"""
    This module contains the models for implimenting retailers.
"""
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.db import models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.retailers.exceptions import (
    MultipleDBCARetailerGroupsExist,
    NoDBCARetailerGroupExists,
)

logger = logging.getLogger(__name__)


class RetailerGroup(models.Model):
    name = models.CharField(max_length=150, unique=True)
    oracle_code = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Retailer Group"

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

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.retailer_group} {self.emailuser}"
