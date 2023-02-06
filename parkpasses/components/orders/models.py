"""
    This module contains the models required for implimenting orders.
"""
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum

from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("items")


class Order(models.Model):
    """A class to represent an order"""

    objects = OrderManager()

    order_number = models.CharField(unique=True, max_length=50, null=False, blank=False)
    uuid = models.CharField(
        unique=True,
        max_length=36,
        null=False,
        blank=False,
        help_text="This is copied from the cart to the order before the cart is deleted. \
            It is also stored in ledger as the booking reference of the basket.",
    )
    invoice_reference = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        help_text="This links the order to the matching invoice in ledger.",
    )
    is_no_payment = models.BooleanField(blank=True, default=False)
    retailer_group = models.ForeignKey(
        RetailerGroup,
        related_name="%(class)s_retailer_group",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    payment_confirmed = models.BooleanField(blank=True, default=False)
    datetime_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        ordering = ["-datetime_created"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_number:
            self.order_number = f"O{self.pk:06d}"
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Order for user: {self.user} (Created: {self.datetime_created})"

    @property
    def total(self):
        if self.items.exists():
            return Decimal(self.items.all().aggregate(Sum("amount"))["amount__sum"])
        return Decimal("0.00")

    @property
    def total_display(self):
        return f"${self.total}"

    @property
    def gst(self):
        gst_calcuation = Decimal(100 / (100 + int(settings.LEDGER_GST)))
        return Decimal(self.total - (self.total * gst_calcuation)).quantize(
            Decimal("0.00")
        )

    @property
    def gst_display(self):
        return f"${self.gst}"

    @property
    def email_user(self):
        return retrieve_email_user(self.user)

    @property
    def invoice_link(self):
        return (
            settings.LEDGER_UI_URL
            + "/ledgergw/invoice-pdf/"
            + settings.LEDGER_API_KEY
            + "/"
            + self.invoice_reference
        )


class OrderItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("order")


class OrderItem(models.Model):
    """A class to represent an order item"""

    objects = OrderItemManager()

    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.PROTECT, null=False, blank=False
    )
    object_id = models.CharField(
        max_length=191, null=True, blank=True
    )  # voucher or pass id
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )  # Voucher or Pass
    description = models.CharField(max_length=150, null=False, blank=False)
    amount = models.DecimalField(
        max_digits=7, decimal_places=2, blank=False, null=False
    )
    oracle_code = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        default=settings.PARKPASSES_DEFAULT_ORACLE_CODE,
    )

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.description} | ${self.amount}"
