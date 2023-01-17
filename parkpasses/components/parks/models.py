"""
    This module contains the models required to impliment parks
    which are relevant for [local park passes].

    These models were created so that the appropriate park groups for a user
    can be presented to them when they enter their postcode.
"""
import logging

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

logger = logging.getLogger(__name__)


class Postcode(models.Model):
    """A class to represent a postcode"""

    postcode = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=4,
        validators=[
            MinLengthValidator(4, "Australian postcodes must contain 4 digits")
        ],
    )

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return str(self.postcode)

    def local_parks(self):
        return ParkGroup.objects.filter(
            lgas__in=self.lgas.values_list("id", flat=True)
        ).distinct()

    def local_parks_name_list(self):
        return self.local_parks().values_list("name", flat=True)

    def local_parks_as_string(self):
        return ", ".join(self.local_parks_name_list())


class Park(models.Model):
    """A class to represent a park"""

    image = models.ImageField(null=True, blank=True)
    name = models.CharField(unique=True, max_length=100, null=False, blank=False)
    display_externally = models.BooleanField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return self.name


class LGAManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("postcodes")


class LGA(models.Model):
    """A class to represent a local goverment area (LGA)"""

    objects = LGAManager()

    name = models.CharField(unique=True, max_length=50, null=False, blank=False)
    postcodes = models.ManyToManyField(Postcode, related_name="lgas", blank=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "LGA"
        verbose_name_plural = "LGAs"

    def __str__(self):
        return self.name


class ParkGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("parks")


class ParkGroup(models.Model):
    """A class to represent a group of parks"""

    name = models.CharField(unique=True, max_length=100, null=False, blank=False)
    oracle_code = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        default=settings.PARKPASSES_DEFAULT_ORACLE_CODE,
        help_text=(
            "This oracle code is for PICA local park passes (Online Sales) ONLY. "
            "Don't enter regional codes here."
        ),
    )
    parks = models.ManyToManyField(
        Park, related_name="park_group", through="Member", blank=True
    )
    lgas = models.ManyToManyField(LGA, related_name="park_group", blank=True)
    display_order = models.SmallIntegerField(unique=True, null=False, blank=False)
    display_externally = models.BooleanField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Park Group"
        verbose_name_plural = "Park Groups"

    def __str__(self):
        return self.name

    @classmethod
    def get_park_groups_by_postcode(self, postcode):
        lga_ids = list(
            LGA.objects.filter(postcodes__postcode=postcode)
            .values_list("id", flat=True)
            .distinct()
        )
        return ParkGroup.objects.filter(lgas__id__in=lga_ids).distinct()

    @classmethod
    def get_park_groups_name_list_by_postcode(self, postcode):
        return self.get_park_group_by_postcode(postcode).values_list("name", flat=True)

    @classmethod
    def get_park_groups_name_list_by_postcode_as_string(self, postcode):
        return ", ".join(self.get_park_group_name_list_by_postcode(postcode))


class MemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("park_group", "park")


class Member(models.Model):
    park_group = models.ForeignKey(ParkGroup, on_delete=models.CASCADE)
    park = models.ForeignKey(Park, on_delete=models.CASCADE)
    display_order = models.SmallIntegerField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Parks ParkGroups"
        verbose_name_plural = "Parks ParkGroups"
        unique_together = (("park_group", "display_order"),)
