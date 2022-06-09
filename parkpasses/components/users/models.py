"""
    This module contains the models required for implimenting discount codes
"""
from django.db import models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.concessions.models import Concession


class UserInformation(models.Model):
    """A class to represent a discount code batch comment"""

    user = models.OneToOneField(EmailUser, on_delete=models.PROTECT)
    concession = models.ForeignKey(
        Concession, on_delete=models.CASCADE, blank=True, null=True
    )
    # Any other park pass specific user data to go here
