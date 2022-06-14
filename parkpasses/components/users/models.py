"""
    This module contains the models required for any custom user information required
    for park passes.

    UserInformation - Allows park passes to store the specific concession type for a user
"""
from django.db import models

from parkpasses.components.concessions.models import Concession
from parkpasses.ledger_api_utils import retrieve_email_user


class UserInformation(models.Model):
    """A class to store any additional user data that is needed specific to parks passes"""

    user = models.IntegerField(null=True, blank=True)  # EmailUserRO
    concession = models.ForeignKey(
        Concession, on_delete=models.PROTECT, blank=True, null=True
    )
    # Any other park pass specific user data to go here

    @property
    def user(self):
        return retrieve_email_user(self.user)
