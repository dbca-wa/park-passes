"""
    This module contains the models required for implimenting orders.

    Once a cart is checked out and payment is successful,
    the cart information will be transferred to an order for
    permanent storage so the user and internal staff can view their
    order.
"""
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from parkpasses.components.discount_codes.models import DiscountCode
from parkpasses.components.passes.models import Pass
from parkpasses.components.users.models import UserInformation
from parkpasses.components.vouchers.models import Voucher
from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("items")


class Order(models.Model):
    """A class to represent an order"""

    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    datetime_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    total = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"Order for user: {self.user} (Created: {self.datetime_created})"

    @property
    def email_user(self):
        return retrieve_email_user(self.user)


class OrderItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("cart")


class OrderItem(models.Model):
    """A class to represent an order item"""

    objects = OrderItemManager()

    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.PROTECT, null=False, blank=False
    )
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
        app_label = "parkpasses"

    def __str__(self):
        return f"Content Type: {self.content_type} | Object ID: {self.object_id} Total Price: {self.get_total_price()}"

    def save(self, *args, **kwargs):
        logger.debug(
            "PARKPASSES_VALID_CART_CONTENT_TYPES = "
            + str(settings.PARKPASSES_VALID_CART_CONTENT_TYPES)
        )
        logger.debug("self.content_type = " + str(self.content_type))
        if str(self.content_type) not in settings.PARKPASSES_VALID_CART_CONTENT_TYPES:

            raise ValueError("A Cart Item can only contain a Voucher or a Pass")
        datetime_item_added = timezone.now()
        logger.debug("self.cart.items = " + str(self.cart.items))
        if not self.cart.datetime_first_added_to and not self.cart.items.count():
            self.cart.datetime_first_added_to = datetime_item_added
        self.cart.datetime_last_added_to = datetime_item_added
        self.cart.save()
        super().save(*args, **kwargs)

    def get_total_price(self):
        model_type = str(self.content_type)
        logger.debug("model_type = " + str(model_type))
        if "parkpasses | voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "parkpasses | pass" == model_type:
            return float(self.get_total_price_pass())

    def get_total_price_pass(self):
        park_pass = Pass.objects.get(pk=self.object_id)
        total_price = park_pass.option.price
        if UserInformation.objects.filter(user=self.cart.user).count():
            user_information = UserInformation.objects.get(user=self.cart.user)
            concession = user_information.concession
            if concession:
                concession_percentage = concession.discount_percentage
                concession_discount = total_price * (concession_percentage / 100)
                total_price += concession_discount

        if self.discount_code:
            logger.debug("self.discount_code = " + str(self.discount_code))
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
            total_price -= discount_code_discount

        if self.voucher:
            if self.voucher.amount >= total_price:
                return 0.00
            else:
                total_price -= self.voucher.amount

        return total_price
