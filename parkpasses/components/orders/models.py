"""
    This module contains the models required for implimenting orders.
"""
import logging

from django.db import models

from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("items")


class Order(models.Model):
    """A class to represent an order"""

    order_number = models.CharField(unique=True, max_length=50, null=True, blank=True)
    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    datetime_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = "parkpasses"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_number:
            self.order_number = f"O{self.pk:06d}"
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Order for user: {self.user} (Created: {self.datetime_created})"

    @property
    def email_user(self):
        return retrieve_email_user(self.user)


class OrderItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("order")


class OrderItem(models.Model):
    """A class to represent an order item"""

    objects = OrderItemManager()

    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.PROTECT, null=False, blank=False
    )
    description = models.CharField(max_length=150, null=False, blank=False)
    amount = models.DecimalField(
        max_digits=7, decimal_places=2, blank=False, null=False
    )

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.description} | ${self.amount}"
