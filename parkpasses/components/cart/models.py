"""
    This module contains the models required for implimenting the shopping cart
"""
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from parkpasses.components.discount_codes.models import DiscountCode
from parkpasses.components.orders.models import Order, OrderItem
from parkpasses.components.passes.models import Pass
from parkpasses.components.users.models import UserInformation
from parkpasses.components.vouchers.models import Voucher
from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class CartManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("items")


class Cart(models.Model):
    """A class to represent a cart"""

    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    datetime_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    datetime_first_added_to = models.DateTimeField(null=True, blank=True)
    datetime_last_added_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"Cart for user: {self.user} (Created: {self.datetime_created})"

    @property
    def email_user(self):
        return retrieve_email_user(self.user)

    @property
    def grand_total(self):
        grand_total = 0.00
        for item in self.items.all():
            grand_total += item.get_total_price()
        return grand_total

    def create_order(self):
        order = Order(user=self.user)
        order.save()
        for cart_item in self.items.all():
            order_item = OrderItem()
            order_item.order = order
            if cart_item.is_voucher_purchase():
                voucher = Voucher.objects.get(pk=cart_item.object_id)
                order_item.description = f"Voucher Puchase: {voucher.voucher_number}"
                order_item.amount = voucher.amount
                order_item.save()
            else:
                park_pass = Pass.objects.get(pk=cart_item.object_id)
                order_item.description = f"Park Pass Puchase: {park_pass.pass_number}"
                order_item.amount = park_pass.option.price
                order_item.save()

                user_information = UserInformation.objects.get(user=self.user)
                if user_information.concession:
                    concession = user_information.concession
                    concession_discount = cart_item.get_concession_discount_as_amount()
                    if concession_discount > 0.00:
                        order_item = OrderItem()
                        order_item.order = order
                        order_item.description = "Concession Discount: "
                        order_item.description += concession.concession_type + " "
                        order_item.description += (
                            user_information.concession_card_number
                        )
                        order_item.amount = -abs(concession_discount)
                        order_item.save()

                if cart_item.discount_code:
                    discount_code_discount = (
                        cart_item.get_discount_code_discount_as_amount()
                    )
                    if discount_code_discount > 0.00:
                        order_item = OrderItem()
                        order_item.order = order
                        order_item.description = (
                            f"Discount Code Applied: {cart_item.discount_code.code}"
                        )
                        order_item.amount = -abs(discount_code_discount)
                        order_item.save()

                if cart_item.voucher:
                    voucher_discount = cart_item.get_voucher_discount_as_amount()
                    if voucher_discount > 0.00:
                        order_item = OrderItem()
                        order_item.order = order
                        order_item.description = (
                            f"Voucher Code Redeemed: {cart_item.voucher.code}"
                        )
                        order_item.amount = -abs(voucher_discount)
                        order_item.save()
        self.delete()


class CartItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("cart")


class CartItem(models.Model):
    """A class to represent a cart item"""

    objects = CartItemManager()

    cart = models.ForeignKey(
        Cart, related_name="items", on_delete=models.CASCADE, null=False, blank=False
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
        unique_together = (("content_type", "object_id"),)
        indexes = (models.Index(fields=["content_type", "object_id"]),)

    def __str__(self):
        return f"Content Type: {self.content_type} | Object ID: {self.object_id} Total Price: {self.get_total_price()}"

    def save(self, *args, **kwargs):
        logger.debug(
            "PARKPASSES_VALID_CART_CONTENT_TYPES = "
            + str(settings.PARKPASSES_VALID_CART_CONTENT_TYPES)
        )
        logger.debug("self.content_type = " + str(self.content_type))
        if str(self.content_type) not in settings.PARKPASSES_VALID_CART_CONTENT_TYPES:
            logger.error(
                f"Attempting to add invalid content type {self.content_type} \
                    to cart {self.cart.pk} for user {self.cart.user}"
            )
            raise ValueError("A Cart Item can only contain a Voucher or a Pass")
        datetime_item_added = timezone.now()
        logger.debug("self.cart.items = " + str(self.cart.items))
        if not self.cart.datetime_first_added_to and not self.cart.items.count():
            self.cart.datetime_first_added_to = datetime_item_added
        self.cart.datetime_last_added_to = datetime_item_added
        self.cart.save()
        super().save(*args, **kwargs)

    def is_voucher_purchase(self):
        return str(self.content_type) == "parkpasses | voucher"

    def is_pass_purchase(self):
        return str(self.content_type) == "parkpasses | pass"

    def get_price_before_discounts(self):
        """Does not take concession, discount code and voucher into consideration"""
        model_type = str(self.content_type)
        logger.debug("model_type = " + str(model_type))
        if "parkpasses | voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "parkpasses | pass" == model_type:
            return Pass.objects.get(pk=self.object_id).option.price

    def get_total_price(self):
        """Takes concession, discount code and voucher into consideration"""
        model_type = str(self.content_type)
        logger.debug("model_type = " + str(model_type))
        if "parkpasses | voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "parkpasses | pass" == model_type:
            return float(self.get_total_price_pass())

    def get_concession_discount_as_amount(self):
        park_pass = Pass.objects.get(pk=self.object_id)
        total_price = park_pass.option.price
        if UserInformation.objects.filter(user=self.cart.user).count():
            user_information = UserInformation.objects.get(user=self.cart.user)
            concession = user_information.concession
            if concession:
                concession_percentage = concession.discount_percentage
                concession_discount = total_price * (concession_percentage / 100)
                return concession_discount
            return 0.00
        else:
            logger.error(
                f"ERROR: The user with id {self.user.id} that is assigned to cart {self.id} does not exist."
            )
        return 0.00

    def get_discount_code_discount_as_amount(self):
        if not self.discount_code:
            return 0.00
        price_before_discounts = self.get_price_before_discounts()
        discount_code_batch = self.discount_code.discount_code_batch
        if discount_code_batch.discount_amount:
            return self.discount_code.discount_code_batch.discount_amount
        else:
            return price_before_discounts * (
                discount_code_batch.discount_percentage / 100
            )

    def get_voucher_discount_as_amount(self):
        if not self.voucher:
            return 0.00
        if 0.00 == self.voucher.amount:
            return 0.00
        price_before_discounts = self.get_price_before_discounts()
        concession_discount_amount = self.get_concession_discount_as_amount()
        discount_code_discount_amount = self.get_discount_code_discount_as_amount()
        remaining_price = (
            price_before_discounts
            - concession_discount_amount
            - discount_code_discount_amount
        )
        if self.voucher.amount >= remaining_price:
            return remaining_price
        else:
            return self.voucher.amount

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
