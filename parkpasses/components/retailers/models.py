"""
    This module contains the models for implimenting retailers.
"""
from django.db import models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser


class RetailerUsers(models.Model):
    """A class to represent the many to many relationship between retailers and email users"""

    retailer_id = models.IntegerField()
    emailuser_id = models.IntegerField()

    class Meta:
        app_label = "parkpasses"
        managed = False
        db_table = "parkpasses_retailer_users"


class Retailer(models.Model):
    """A class to represent a retailer"""

    name = models.CharField(max_length=100, null=False, blank=False)
    users = models.ManyToManyField(
        EmailUser,
        db_table="parkpasses_retailer_users",
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        app_label = "parkpasses"


Retailer.users.through._meta.get_field("emailuserro_id").column = "emailuser_id"
