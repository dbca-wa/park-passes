"""
    This module contains the models required for implimenting the shopping cart
"""
import logging
import uuid
from copy import copy
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.concessions.models import ConcessionUsage
from parkpasses.components.discount_codes.models import DiscountCodeUsage
from parkpasses.components.orders.models import Order, OrderItem
from parkpasses.components.passes.models import Pass, RACDiscountUsage
from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.components.vouchers.models import Voucher, VoucherTransaction
from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class CartManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("items")


class Cart(models.Model):
    """A class to represent a cart"""

    user = models.IntegerField(null=True, blank=True)  # EmailUserRO
    datetime_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    uuid = models.CharField(max_length=36, blank=True, null=True)
    is_no_payment = models.BooleanField(blank=True, default=False)
    retailer_group = models.ForeignKey(
        RetailerGroup,
        related_name="%(class)s_retailer_group",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    datetime_first_added_to = models.DateTimeField(null=True, blank=True)
    datetime_last_added_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"Cart for user: {self.user} (Created: {self.datetime_created})"

    @classmethod
    def get_or_create_cart(self, request):
        logger.info(
            f"Calling get_or_create_cart for user: {request.user.id} ({request.user})"
        )
        cart_id = request.session.get("cart_id", None)
        logger.info(f"cart_id = {cart_id}")
        if cart_id and Cart.objects.filter(id=cart_id).exists():
            logger.info(
                f"Cart with cart_id of {cart_id} exists.",
            )
            cart = Cart.objects.get(id=cart_id)
            # There is an edge case here where a user has a cart in db but is browsing the site
            # anonymously and adds one or more items to their cart. When they log in we need to move
            # the items from their anonymous cart to their already existing cart...
            if Cart.objects.filter(user=request.user.id).exclude(id=cart.id).exists():
                logger.info(
                    f"Anonymous cart items exist for user: {request.user.id} ({request.user})",
                )
                anon_cart = copy(cart)
                logger.info(
                    f"Selecting existing cart for user: {request.user.id} ({request.user}).",
                )
                cart = (
                    Cart.objects.filter(user=request.user.id)
                    .exclude(id=cart.id)
                    .order_by("user", "-datetime_created")
                    .first()
                )
                if anon_cart.items.all().exists():
                    logger.info(
                        f"Assigning anonymous cart items to existing cart: {cart}",
                    )
                    anon_cart.items.all().update(cart=cart)
                    logger.info(
                        f"Deleting anonymous cart: {anon_cart}",
                    )
                    anon_cart.delete()
                    logger.info(
                        f"Anonymous cart: {anon_cart} deleted.",
                    )
            else:
                logger.info(
                    f"No Anonymous cart items exists for user: {request.user.id} ({request.user})",
                )
                if not cart.user:
                    logger.info(
                        f"Assigning user: {request.user.id} ({request.user}) to cart: {cart}.",
                    )
                    cart.user = request.user.id
                    logger.info(
                        f"Saving cart: {cart}",
                    )
                    cart.save()
                    logger.info(
                        f"Cart: {cart} saved.",
                    )
        else:
            logger.info(
                f"No cart with id: {cart_id} exists for user: {request.user.id} ({request.user})",
            )
            logger.info(
                f"Checking if user: {request.user.id} ({request.user}) has any carts.",
            )
            if Cart.objects.filter(user=request.user.id).exists():
                cart = (
                    Cart.objects.filter(user=request.user.id)
                    .order_by("user", "-datetime_created")
                    .first()
                )
            else:
                logger.info(
                    f"User: {request.user.id} ({request.user}) has no carts. Creating new cart.",
                )
                cart = Cart.objects.create()
                logger.info(
                    f"New cart: {cart} created.",
                )
        cart_item_count = CartItem.objects.filter(cart=cart).count()
        request.session["cart_item_count"] = cart_item_count
        logger.info(
            f"cart_item_count session variable for cart: {cart} set to {cart_item_count}"
        )
        request.session["cart_id"] = cart.id
        logger.info(f"cart_id session variable for cart: {cart} set to {cart.id}")

        logger.info(f"Returning cart: {cart} to caller")
        return cart

    def set_user_for_cart_and_items(self, user_id):
        logger.info(f"Calling set_user_for_cart_and_items for user: {user_id}.")
        self.user = user_id
        logger.info(f"Assigning user with id: {user_id} to cart: {self}")
        self.save()
        logger.info(f"Cart: {self} saved.")

        voucher_ids = list(CartItem.vouchers.filter(cart=self))
        vouchers = Voucher.objects.filter(id__in=voucher_ids)
        if vouchers:
            logger.info(
                f"Vouchers exist for cart: {self}.",
            )
            for voucher in vouchers:
                voucher.purchaser = user_id
                logger.info(
                    f"Voucher: {voucher} purchaser field set to: {user_id}.",
                )
                logger.info(
                    f"Saving Voucher: {voucher}",
                )
                voucher.save()
                logger.info(
                    f"Voucher: {voucher} saved.",
                )

        park_pass_ids = list(CartItem.passes.filter(cart=self))
        park_passes = Pass.objects.filter(id__in=park_pass_ids)
        if park_passes:
            logger.info(
                f"Park passes exist for cart: {self}.",
            )
            for park_pass in park_passes:
                logger.info(
                    f"Park pass: {park_pass} user field set to: {user_id}.",
                )
                logger.info(
                    f"Saving Park pass: {park_pass}",
                )
                park_pass.user = user_id
                park_pass.save()
                logger.info(
                    f"Park pass: {park_pass} saved.",
                )

    @property
    def email_user(self):
        return retrieve_email_user(self.user)

    @property
    def grand_total(self):
        grand_total = Decimal(0.00)
        for item in self.items.all():
            grand_total += Decimal(item.get_total_price())
        return grand_total.quantize(Decimal("0.01"))

    def create_order(
        self,
        save_order_to_db_and_delete_cart=False,
        invoice_reference=None,
    ):
        """This method can create an order and order items from a cart (and cart items)
        By default it doesn't add this order to the database. This is so we can use the
        order to submit to leger and wait until that order is confirmed before we add
        the order to the park passes database.
        """
        logger.info(f"Creating order from cart: {self}")
        logger.info(
            f"Saving order to database = {str(save_order_to_db_and_delete_cart)}"
        )
        if Order.objects.filter(uuid=self.uuid).exists():
            logger.info(
                f"Order with uuid {self.uuid} already exists.",
            )
            order = Order.objects.get(uuid=self.uuid)
            logger.info(
                f"Order: {str(order)} selected.",
            )
            order.user = self.user
        else:
            logger.info(
                f"Order with uuid {self.uuid} doesn't exist.",
            )
            order = Order(user=self.user)
            logger.info(
                f"Order {str(order)} created.",
            )

        order_items = []
        if save_order_to_db_and_delete_cart:
            if not self.uuid or not invoice_reference:
                raise ValueError(
                    "If save_order_to_db_and_delete_cart is True then \
                    the cart must have a uuid and an invoice_reference must be passed in."
                )
            logger.info("Populating Order")
            order.uuid = self.uuid
            order.invoice_reference = invoice_reference
            order.is_no_payment = self.is_no_payment
            if self.retailer_group:
                order.retailer_group = self.retailer_group
            else:
                order.retailer_group = RetailerGroup.get_dbca_retailer_group()
            order.save()
            logger.info(
                "Transferring cart items to order items.",
            )
        for cart_item in self.items.all():
            logger.info(
                f"Creating new order item with data from cart item: {cart_item}.",
            )
            order_item = OrderItem()
            order_item.object_id = cart_item.object_id
            order_item.content_type_id = cart_item.content_type_id
            order_item.order = order
            order_item.oracle_code = cart_item.oracle_code
            if cart_item.is_voucher_purchase():
                logger.info(
                    "Cart item is a voucher purchase.",
                )
                voucher = Voucher.objects.get(pk=cart_item.object_id)
                order_item.description = CartUtils.get_voucher_purchase_description(
                    voucher.voucher_number
                )
                order_item.amount = voucher.amount
                order_items.append(order_item)
                if save_order_to_db_and_delete_cart:
                    voucher.in_cart = False
                    voucher.save()
                    order_item.save()
                    logger.info(
                        f"Order item {order_item} saved.",
                    )

            else:
                logger.info(
                    "Cart item is a park pass purchase.",
                )
                park_pass = Pass.objects.get(pk=cart_item.object_id)
                order_item.description = CartUtils.get_pass_purchase_description(
                    park_pass.pass_number
                )
                order_item.amount = park_pass.option.price
                order_items.append(order_item)
                if save_order_to_db_and_delete_cart:
                    park_pass.in_cart = False
                    park_pass.save()
                    order_item.save()
                    logger.info(
                        f"Order item {order_item} saved.",
                    )

                if cart_item.rac_discount_usage:
                    logger.info(
                        f"RAC Discount Usage exists for cart_item {cart_item}.",
                    )
                    # A RAC discount is being applied to this pass purchase
                    rac_discount_amount = cart_item.rac_discount_usage.discount_amount
                    if rac_discount_amount > Decimal(0.00):
                        logger.info(
                            "RAC discount is greater than 0.00. Proceeding.",
                        )
                        order_item = OrderItem()
                        order_item.order = order
                        order_item.description = (
                            CartUtils.get_rac_discount_description()
                        )
                        logger.info(
                            f"RAC order item description: {order_item.description}",
                        )
                        order_item.amount = -abs(rac_discount_amount)
                        order_items.append(order_item)
                        if save_order_to_db_and_delete_cart:
                            order_item.save()
                            logger.info(
                                f"Order item {order_item} saved.",
                            )
                elif cart_item.concession_usage:
                    logger.info(
                        f"Concession Usage exists for cart_item {cart_item}.",
                    )
                    # A concession discount is being applied to this pass purchase
                    concession = cart_item.concession_usage.concession
                    concession_discount = concession.discount_as_amount(
                        park_pass.option.price
                    )
                    if concession_discount > Decimal(0.00):
                        logger.info(
                            "Concession discount is greater than 0.00. Proceeding.",
                        )
                        order_item = OrderItem()
                        order_item.order = order
                        order_item.description = CartUtils.get_concession_description(
                            concession.concession_type
                        )
                        logger.info(
                            f"Concession order item description: {order_item.description}",
                        )

                        # The ledger checkout doesn't round a negative balance to zero so in order to avoid
                        # processing a refund we have to make sure the discount is no more than the total pass price
                        if concession_discount >= park_pass.price:
                            order_item.amount = -abs(
                                park_pass.price.quantize(Decimal("0.01"))
                            )
                        else:
                            order_item.amount = -abs(
                                concession_discount.quantize(Decimal("0.01"))
                            )
                        logger.info(
                            f"Concession order item amount: {order_item.amount}",
                        )

                        order_items.append(order_item)
                        logger.info(
                            "Concession order item appended to order items.",
                        )
                        if save_order_to_db_and_delete_cart:
                            order_item.save()
                            logger.info(
                                f"Concession order item saved: {order_item}.",
                            )

                if cart_item.discount_code_usage:
                    logger.info(
                        f"Discount Code Usage exists for cart_item {cart_item}.",
                    )
                    # A discount code is being applied to this pass purchase
                    discount_code_discount = (
                        cart_item.get_discount_code_discount_as_amount()
                    )
                    if discount_code_discount > 0.00:
                        logger.info(
                            "Discount Code discount is greater than 0.00. Proceeding.",
                        )
                        order_item = OrderItem()
                        order_item.order = order
                        order_item.description = (
                            CartUtils.get_discount_code_description(
                                cart_item.discount_code_usage.discount_code.code
                            )
                        )
                        logger.info(
                            f"Discount Code order item description: {order_item.description}",
                        )

                        # The ledger checkout doesn't round a negative balance to zero so in order to avoid
                        # processing a refund we have to make sure the discount is no more than the total pass price
                        if discount_code_discount >= park_pass.price:
                            order_item.amount = -abs(
                                park_pass.price.quantize(Decimal("0.01"))
                            )
                        else:
                            order_item.amount = -abs(
                                discount_code_discount.quantize(Decimal("0.01"))
                            )
                        logger.info(
                            f"Discount Code order item amount: {order_item.amount}",
                        )

                        order_items.append(order_item)
                        logger.info(
                            "Discount Code order item appended to order items.",
                        )

                        if save_order_to_db_and_delete_cart:
                            order_item.save()
                            logger.info(
                                f"Discount Code order item saved: {order_item}.",
                            )

                if cart_item.voucher_transaction:
                    logger.info(
                        f"Voucher Transaction exists for cart_item {cart_item}.",
                    )
                    # A voucher is being used for this pass purchase
                    voucher_transaction_balance = (
                        cart_item.voucher_transaction.balance()
                    )
                    order_item = OrderItem()
                    order_item.order = order
                    order_item.description = CartUtils.get_voucher_code_description(
                        cart_item.voucher_transaction.voucher.code
                    )
                    logger.info(
                        f"Voucher transaction order item description: {order_item.description}",
                    )

                    order_item.amount = voucher_transaction_balance.quantize(
                        Decimal("0.01")
                    )
                    logger.info(
                        f"Voucher transaction order item amount: {order_item.amount}",
                    )

                    order_items.append(order_item)
                    if save_order_to_db_and_delete_cart:
                        order_item.save()
                        logger.info(
                            f"Voucher transaction order item saved: {order_item}.",
                        )

        if save_order_to_db_and_delete_cart:
            logger.info(f"Deleting Cart {self}.")
            self.delete()
            logger.info("Cart Deleted.")

        logger.info(f"Returning order {order} and order items.")
        return order, order_items

    def save(self, *args, **kwargs):
        logger.info(f"Saving Cart: {self}.")
        if not self.uuid:
            logger.info("Cart has no uuid")
            self.uuid = uuid.uuid4()
            logger.info(
                f"Cart assigned uuid: {self.uuid}",
            )
        logger.info(f"Saving Cart: {self}.")
        super().save(*args, **kwargs)
        logger.info("Cart Saved.")


class CartItemVoucherManager(models.Manager):
    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(Voucher)
        return (
            super()
            .get_queryset()
            .filter(content_type=content_type)
            .values_list("object_id", flat=True)
        )


class CartItemPassManager(models.Manager):
    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(Pass)
        return (
            super()
            .get_queryset()
            .filter(content_type=content_type)
            .values_list("object_id", flat=True)
        )


class CartItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("cart")


class CartItem(models.Model):
    """A class to represent a cart item"""

    objects = CartItemManager()

    vouchers = CartItemVoucherManager()

    passes = CartItemPassManager()

    cart = models.ForeignKey(
        Cart, related_name="items", on_delete=models.CASCADE, null=False, blank=False
    )
    object_id = models.CharField(max_length=191)  # voucher or pass id
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )  # Voucher or Pass
    rac_discount_usage = models.ForeignKey(
        RACDiscountUsage, on_delete=models.PROTECT, null=True, blank=True
    )
    concession_usage = models.ForeignKey(
        ConcessionUsage, on_delete=models.PROTECT, null=True, blank=True
    )
    discount_code_usage = models.ForeignKey(
        DiscountCodeUsage, on_delete=models.PROTECT, null=True, blank=True
    )
    voucher_transaction = models.ForeignKey(
        VoucherTransaction, on_delete=models.PROTECT, null=True, blank=True
    )
    oracle_code = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        default=settings.PARKPASSES_DEFAULT_ORACLE_CODE,
    )
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "parkpasses"
        unique_together = (("content_type", "object_id"),)
        indexes = (models.Index(fields=["content_type", "object_id"]),)
        ordering = ["datetime_created", "object_id"]

    def __str__(self):
        return f"Content Type: {self.content_type} | Object ID: {self.object_id} Total Price: {self.get_total_price()}"

    def save(self, *args, **kwargs):
        logger.info(f"Saving Cart Item: {self}.")

        if str(self.content_type) not in settings.PARKPASSES_VALID_CART_CONTENT_TYPES:
            logger.error(
                f"Attempting to add invalid content type {self.content_type} \
                    to cart {self.cart.pk} for user {self.cart.user}",
            )
            raise ValueError(
                "A Cart Item can only contain a Voucher or a Pass",
            )
        datetime_item_added = timezone.now()
        logger.info("Checking if parent Cart has been added to in the past?")
        if not self.cart.datetime_first_added_to and not self.cart.items.count():
            logger.info(
                "Parent Cart has not been added to in the past.",
            )
            self.cart.datetime_first_added_to = datetime_item_added
            logger.info(
                f"Assigned date time first added to: {self.cart.datetime_first_added_to}.",
            )

        self.cart.datetime_last_added_to = datetime_item_added
        logger.info(
            f"Assigned date time last added to: {self.cart.datetime_last_added_to}."
        )

        logger.info(f"Saving parent Cart: {self.cart}.")
        self.cart.save()
        logger.info("Parent Cart saved.")

        logger.info(f"Saving Cart Item: {self}.")
        super().save(*args, **kwargs)
        logger.info("Cart Item saved.")

    def is_voucher_purchase(self):
        return "parkpasses | voucher" == str(self.content_type)

    def is_pass_purchase(self):
        return "parkpasses | pass" == str(self.content_type)

    def delete(self, *args, **kwargs):
        logger.info(f"Deleting Cart Item: {self}.")
        if self.is_voucher_purchase():
            logger.info(
                "Cart Item is a voucher purchase.",
            )
            if Voucher.objects.filter(id=self.object_id, in_cart=True).exists():
                logger.info(
                    f"Selected Voucher with id: {self.object_id}.",
                )
                voucher = Voucher.objects.get(id=self.object_id)
                logger.info(
                    f"Deleting associated voucher: {voucher}.",
                )
                voucher.delete()
                logger.info(
                    "Associated voucher deleted.",
                )

        elif self.is_pass_purchase():
            logger.info(
                "Cart Item is a Park Pass purchase.",
            )
            if Pass.objects.filter(id=self.object_id, in_cart=True).exists():
                logger.info(
                    f"Selected Pass with id: {self.object_id}.",
                )
                park_pass = Pass.objects.get(id=self.object_id)

                logger.info(
                    "Removing concession usage, discount code usage and voucher transaction from cart item.",
                )
                self.concession_usage = None
                self.discount_code_usage = None
                self.voucher_transaction = None
                logger.info(
                    "Concession usage, discount code usage and voucher transaction removed.",
                )

                logger.info(
                    f"Saving cart item: {self}.",
                )
                self.save()
                logger.info("Cart Item saved.")

                logger.info(
                    "Deleting concession usage, discount code usage and voucher transaction.",
                )
                ConcessionUsage.objects.filter(park_pass=park_pass).delete()
                DiscountCodeUsage.objects.filter(park_pass=park_pass).delete()
                VoucherTransaction.objects.filter(park_pass=park_pass).delete()
                logger.info(
                    "Doncession usage, discount code usage and voucher transaction deleted.",
                )

                logger.info(
                    f"Deleting park pass: {park_pass}.",
                )
                park_pass.delete()
                logger.info("Park Pass deleted.")

        logger.info("Returning from Cart Item delete.")
        return super().delete(*args, **kwargs)

    def get_price_before_discounts(self):
        """Does not take concession, discount code and voucher into consideration"""
        model_type = str(self.content_type)
        if "parkpasses | voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "parkpasses | pass" == model_type:
            return Pass.objects.get(pk=self.object_id).option.price

    def get_concession_price(self):
        model_type = str(self.content_type)
        if "parkpasses | voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "parkpasses | pass" == model_type:
            park_pass = Pass.objects.get(pk=self.object_id)
            return park_pass.price_after_concession_applied

    def get_total_price(self):
        """Takes concession, discount code and voucher into consideration"""
        model_type = str(self.content_type)
        if "parkpasses | voucher" == model_type:
            return Voucher.objects.get(pk=self.object_id).amount
        elif "parkpasses | pass" == model_type:
            if Pass.objects.filter(pk=self.object_id).exists():
                park_pass = Pass.objects.get(pk=self.object_id)
                return Decimal(park_pass.price_after_all_discounts)
            return Decimal(0.00)

    # TODO: DRY These should not be in this file. Move them to their respetive objects
    # then use this as convenience methods that just call those methods on the other objects
    def get_concession_discount_as_amount(self):
        if not self.concession_usage:
            return Decimal(0.00)
        concession = self.concession_usage.concession
        total_price = self.get_price_before_discounts()
        return Decimal(total_price * (concession.discount_percentage / 100))

    def get_discount_code_discount_as_amount(self):
        if not self.discount_code_usage:
            return Decimal(0.00)
        price_before_discounts = self.get_price_before_discounts()
        discount_code_batch = self.discount_code_usage.discount_code.discount_code_batch
        if discount_code_batch.discount_amount:
            return (
                self.discount_code_usage.discount_code.discount_code_batch.discount_amount
            )
        else:
            return price_before_discounts * (
                discount_code_batch.discount_percentage / 100
            )

    def get_voucher_discount_as_amount(self):
        if not self.voucher_transaction.voucher:
            return Decimal(0.00)
        if Decimal(0.00) >= self.voucher_transaction.voucher.amount:
            return Decimal(0.00)
        price_before_discounts = self.get_price_before_discounts()
        concession_discount_amount = self.get_concession_discount_as_amount()
        discount_code_discount_amount = self.get_discount_code_discount_as_amount()
        remaining_price = (
            price_before_discounts
            - concession_discount_amount
            - discount_code_discount_amount
        )
        if self.voucher_transaction.voucher.amount >= remaining_price:
            return remaining_price
        else:
            return self.voucher_transaction.voucher.amount
