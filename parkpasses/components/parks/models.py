"""
    This module contains the models required to impliment parks
    which are relevant for [local park passes].

    A postcode can have mutiple local parks associated with it.
    A local park can have mulitple postcodes it is relevant to.
"""
from django.core.validators import MinLengthValidator
from django.db import models


class Park(models.Model):
    """A class to represent a park"""

    image = models.ImageField()
    name = models.CharField()
    display_order = models.SmallIntegerField()
    display_externally = models.BooleanField()


class Postcode(models.Model):
    """A class to represent a postcode"""

    parks = models.ManyToManyField(Park)
    postcode = models.SmallIntegerField(
        null=False,
        blank=False,
        max_length=4,
        validators=[
            MinLengthValidator(4, "Australian postcodes must contain 4 digits")
        ],
    )
