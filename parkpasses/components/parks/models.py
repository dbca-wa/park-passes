"""
    This module contains the models required to impliment parks
    which are relevant for [local park passes].

    A postcode can have mutiple local parks associated with it.
    A local park can have mulitple postcodes it is relevant to.
"""
from django.core.validators import MinLengthValidator
from django.db import models


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


class Park(models.Model):
    """A class to represent a park"""

    postcodes = models.ManyToManyField(Postcode, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    name = models.CharField(unique=True, max_length=100, null=False, blank=False)
    display_order = models.SmallIntegerField(unique=True, null=False, blank=False)
    display_externally = models.BooleanField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return self.name
