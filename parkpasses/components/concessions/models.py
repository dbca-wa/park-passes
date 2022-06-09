"""
    This module contains the models for implimenting concessions.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class Concession(models.Model):
    """A class to represent a concession"""

    concession_type = models.CharField(unique=True, max_length=50)
    discount_percentage = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        blank=False,
        null=False,
        validators=PERCENTAGE_VALIDATOR,
    )
