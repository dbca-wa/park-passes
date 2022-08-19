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

    user = models.IntegerField(unique=True, null=False, blank=False)  # EmailUserRO
    concession = models.ForeignKey(
        Concession, on_delete=models.PROTECT, blank=True, null=True
    )
    concession_card_number = models.CharField(max_length=50, null=True, blank=True)
    # Any other park pass specific user data to go here

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "user Information"

    @property
    def email_user(self):
        return retrieve_email_user(self.user)

    @classmethod
    def get_concession_by_user_id(self, user_id):
        if UserInformation.objects.filter(user=user_id).count():
            return UserInformation.objects.get(user=user_id).concession
        return None
