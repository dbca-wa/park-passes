"""
    This module contains the models required for implimenting the shopping cart
"""
from django.db import models

from parkpasses.components.passes.models import Pass
from parkpasses.components.vouchers.models import Voucher
from parkpasses.ledger_api_utils import retrieve_email_user


class Cart(models.Model):
    """A class to represent a cart"""

    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    datetime_first_added_to = models.DateTimeField()
    datetime_last_added_to = models.DateTimeField()

    @property
    def user(self):
        return retrieve_email_user(self.user)


class CartItem(models.Model):
    """A class to represent a cart item"""

    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, null=False, blank=False)
    park_pass = models.ForeignKey(Pass, on_delete=models.PROTECT, null=True, blank=True)
    voucher = models.ForeignKey(
        Voucher, on_delete=models.PROTECT, null=True, blank=True
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)

    class Meta:
        """Meta for cart item - used here to add a custom constraint

        A cart item must have either a park pass or a voucher attached to
        be valid.
        """

        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_park_pass_or_voucher",
                check=(
                    models.Q(park_pass__isnull=True, voucher__isnull=False)
                    | models.Q(park_pass__isnull=False, voucher__isnull=True)
                ),
            )
        ]
