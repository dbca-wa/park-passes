"""
    This module contains the models required for implimenting the shopping cart
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models

from parkpasses.components.discount_codes.models import DiscountCode
from parkpasses.components.passes.models import Pass
from parkpasses.components.users.models import UserInformation
from parkpasses.components.vouchers.models import Voucher
from parkpasses.ledger_api_utils import retrieve_email_user


class Cart(models.Model):
    """A class to represent a cart"""

    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    datetime_first_added_to = models.DateTimeField()
    datetime_last_added_to = models.DateTimeField()

    class Meta:
        app_label = "parkpasses"

    @property
    def user(self):
        return retrieve_email_user(self.user)


class CartItem(models.Model):
    """A class to represent a cart item"""

    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, null=False, blank=False)
    object_id = models.CharField(max_length=191)  # voucher or pass id
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )  # Voucher or Pass
    voucher = models.ForeignKey(
        Voucher, on_delete=models.PROTECT, null=True, blank=True
    )
    discount_code = models.ForeignKey(
        DiscountCode, on_delete=models.PROTECT, null=True, blank=True
    )

    class Meta:
        """Meta for cart item - used here to add a custom constraint

        A cart item must have either a park pass or a voucher attached to
        be valid.
        """

        app_label = "parkpasses"
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_park_pass_or_voucher",
                check=(
                    models.Q(park_pass__isnull=True, voucher__isnull=False)
                    | models.Q(park_pass__isnull=False, voucher__isnull=True)
                ),
            )
        ]

    def get_total_price(self):
        model_type = self.content_type.model
        if "Voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "Pass" == model_type:
            return self.get_total_price_pass()
        else:
            raise ValueError("A Cart Item can only contain a Voucher or a Pass")

    def get_total_price_pass(self):
        park_pass = Pass.objects.get(pk=self.object_id)
        total_price = park_pass.option.price
        user_information = UserInformation.objects.get(pk=self.cart.user)
        concession = user_information.concession
        if concession:
            concession_percentage = concession.discount_percentage
            concession_discount = total_price * (concession_percentage / 100)
            total_price += concession_discount

        if self.discount_code:
            discount_code_batch = self.discount_code.discount_code_batch
            if discount_code_batch.discount_percentage:
                discount_code_discount = total_price * (
                    discount_code_batch.discount_percentage / 100
                )
            else:
                discount_code_discount = (
                    total_price - discount_code_batch.discount_amount
                )

            if total_price - discount_code_discount < 0.00:
                return 0.00

        if self.voucher:
            if self.voucher.amount >= total_price:
                return 0.00
            else:
                total_price -= self.voucher.amount

        return total_price
