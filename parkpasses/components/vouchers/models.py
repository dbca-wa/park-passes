"""
    This module contains the models required for implimenting vouchers

    Each voucher may have one or more voucher transactions which allow
    vouchers to retain a positive balance so they can be used to pay
    for multiple seperate transactions.
"""
import datetime
import uuid

from django.db import models

from parkpasses import settings
from parkpasses.ledger_api_utils import retrieve_email_user


class Voucher(models.Model):
    """A class to represent a voucher"""

    voucher_number = models.CharField(max_length=10, blank=True)
    purchaser = models.IntegerField(null=False, blank=False)  # EmailUserRO
    recipient_name = models.CharField(max_length=50, null=False, blank=False)
    recipient_email = models.EmailField(null=False, blank=False)
    datetime_to_email = models.DateTimeField(null=False)
    personal_message = models.TextField(null=False)
    amount = models.DecimalField(
        max_digits=7, decimal_places=2, blank=False, null=False
    )
    expiry = models.DateTimeField(null=False)
    code = models.CharField(max_length=10)
    pin = models.DecimalField(max_digits=6, decimal_places=0, blank=False, null=False)
    datetime_purchased = models.DateTimeField(auto_now_add=True)
    NEW = "N"
    DELIVERED = "D"
    NOT_DELIVERED = "ND"
    PROCESSING_STATUS_CHOICES = [
        (NEW, "New"),
        (DELIVERED, "Delivered"),
        (NOT_DELIVERED, "Not Delivered"),
    ]
    processing_status = models.CharField(
        max_length=2,
        choices=PROCESSING_STATUS_CHOICES,
        default=NEW,
    )

    class Meta:
        app_label = "parkpasses"
        indexes = (models.Index(fields=["code"]),)

    def __str__(self):
        return self.voucher_number

    @property
    def purchaser(self):
        return retrieve_email_user(self.purchaser)

    @property
    def has_expired(self):
        if datetime.datetime.now() >= self.expiry:
            return True
        return False

    def get_remaining_balance(self):
        remaining_balance = self.amount
        for transaction in self.transactions:
            if transaction.credit > 0.00:
                remaining_balance += transaction.credit
            if transaction.debit < 0.00:
                remaining_balance -= transaction.debit
        if remaining_balance > self.amount:
            raise Exception(
                "The balance of transactions for this voucher are greater than the amount of the voucher."
            )
        if remaining_balance < 0.00:
            raise Exception(
                "The balance of transactions for this voucher are below 0.00."
            )
        return remaining_balance

    @classmethod
    def get_new_voucher_code(self):
        return str(uuid.uuid4()).upper()[:8]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.get_new_voucher_code()
        if not self.expiry:
            self.expiry = datetime.datetime.now() + datetime.timedelta(
                days=settings.PARKPASSES_VOUCHER_EXPIRY_IN_DAYS
            )
        super().save(*args, **kwargs)
        if not self.voucher_number:
            voucher_number = f"V{self.pk:06d}"
            self.voucher_number = voucher_number
            super().save(*args, **kwargs)


class VoucherTransaction(models.Model):
    """A class to represent a voucher transaction"""

    voucher = models.ForeignKey(
        Voucher, related_name="transactions", on_delete=models.PROTECT
    )
    credit = models.DecimalField(
        max_digits=7, decimal_places=2, blank=False, null=False
    )
    debit = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"Credit: {self.credit} | Debit:{self.debit}"
