"""
    This module contains the models required for implimenting vouchers

    Each voucher may have one or more voucher transactions which allow
    vouchers to retain a positive balance so they can be used to pay
    for multiple seperate transactions.
"""
import logging
import random
import uuid
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from parkpasses import settings
from parkpasses.components.passes.models import Pass
from parkpasses.components.vouchers.emails import VoucherEmails
from parkpasses.components.vouchers.exceptions import (
    RemainingBalanceExceedsVoucherAmountException,
    RemainingVoucherBalanceLessThanZeroException,
    SendVoucherRecipientEmailNotificationFailed,
)
from parkpasses.ledger_api_utils import retrieve_email_user

logger = logging.getLogger(__name__)


class VoucherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("transactions")


class Voucher(models.Model):
    """A class to represent a voucher"""

    objects = VoucherManager()

    voucher_number = models.CharField(max_length=10, blank=True)
    purchaser = models.IntegerField(null=True, blank=True)  # EmailUserRO
    recipient_name = models.CharField(max_length=50, null=False, blank=False)
    recipient_email = models.EmailField(null=False, blank=False)
    datetime_to_email = models.DateTimeField(null=False)
    personal_message = models.TextField(null=False)
    amount = models.DecimalField(
        max_digits=7, decimal_places=2, blank=False, null=False
    )
    expiry = models.DateTimeField(null=False)
    code = models.CharField(unique=True, max_length=10)
    pin = models.CharField(max_length=6, blank=False, null=False)
    datetime_purchased = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)
    NEW = "N"
    NOT_DELIVERED_TO_PURCHASER = "NDP"
    PURCHASER_NOTIFIED = "PN"
    NOT_DELIVERED_TO_RECIPIENT = "NDR"
    DELIVERED_TO_RECIPIENT = "DR"

    PROCESSING_STATUS_CHOICES = [
        (NEW, "New"),
        (NOT_DELIVERED_TO_PURCHASER, "Not Delivered to Purchaser"),
        (PURCHASER_NOTIFIED, "Purchaser Notified"),
        (NOT_DELIVERED_TO_RECIPIENT, "Not Delivered to Recipient"),
        (DELIVERED_TO_RECIPIENT, "Delivered to Recipient"),
    ]
    processing_status = models.CharField(
        max_length=3,
        choices=PROCESSING_STATUS_CHOICES,
        default=NEW,
    )
    in_cart = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        app_label = "parkpasses"
        indexes = (models.Index(fields=["code"]),)
        ordering = ["-id"]

    def __str__(self):
        return f"{self.voucher_number} (${self.amount})"

    @property
    def get_purchaser(self):
        return retrieve_email_user(self.purchaser)

    @property
    def has_expired(self):
        if timezone.now() >= self.expiry:
            return True
        return False

    @property
    def remaining_balance(self):
        remaining_balance = self.amount
        for voucher_transaction in self.transactions.all():
            if voucher_transaction.credit > 0.00:
                remaining_balance += voucher_transaction.credit
            if voucher_transaction.debit > 0.00:
                remaining_balance -= voucher_transaction.debit
        if remaining_balance > self.amount:
            exception_message = (
                f"The remaining balance of {remaining_balance} for voucher with id"
                f"{self.id} is greater than the amount of the voucher."
            )
            logger.error(exception_message)
            raise RemainingBalanceExceedsVoucherAmountException(exception_message)
        if remaining_balance < 0.00:
            exception_message = (
                f"The remaining balance of {remaining_balance}"
                f"for voucher with id {self.id} is below 0.00."
            )
            logger.error(exception_message)
            raise RemainingVoucherBalanceLessThanZeroException(exception_message)
        return remaining_balance

    def balance_available_for_purchase(self, park_pass_price):
        if self.has_expired:
            return Decimal(0.00)

        if Decimal(0.00) >= self.remaining_balance:
            return Decimal(0.00)

        if self.remaining_balance >= park_pass_price:
            return park_pass_price

        return self.remaining_balance

    @classmethod
    def get_new_voucher_code(self):
        is_voucher_code_unique = False
        while not is_voucher_code_unique:
            voucher_code = str(uuid.uuid4()).upper()[:8]
            if not Voucher.objects.filter(code=voucher_code).exists():
                is_voucher_code_unique = True
        return voucher_code

    @classmethod
    def get_new_pin(self):
        return f"{random.randint(0,999999):06d}"

    @classmethod
    def is_valid(self, code, pin):
        """To return True the voucher must:

        - have a code of length 8
        - have a pin of length 6
        - exist
        - have not expired yet
        - have a non zero balance

        """
        if 8 != len(code):
            return False
        if 6 != len(pin):
            return False
        if not Voucher.objects.filter(code=code, pin=pin).exists():
            return False

        discount_code = Voucher.objects.get(code=code, pin=pin)
        if discount_code.has_expired:
            return False

        if 0.00 >= discount_code.remaining_balance:
            return False

        return True

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.get_new_voucher_code()
        if not self.pin:
            self.pin = self.get_new_pin()
        if not self.expiry:
            self.expiry = timezone.now() + timezone.timedelta(
                days=settings.PARKPASSES_VOUCHER_EXPIRY_IN_DAYS
            )
        super().save(*args, **kwargs)
        if not self.voucher_number:
            self.voucher_number = f"V{self.pk:06d}"

        if not self.in_cart:
            if self.processing_status in [
                Voucher.NEW,
            ]:
                self.send_voucher_purchase_notification_email()
            if self.datetime_to_email.date() == timezone.now().date():
                self.send_voucher_sent_notification_emails()

        super().save(force_update=True)

    def send_voucher_purchase_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += "send_voucher_purchase_notification_email for Voucher with id {} at {}. Exception {}"
        with transaction.atomic():
            try:
                VoucherEmails.send_voucher_purchaser_purchased_notification_email(self)
                self.processing_status = Voucher.PURCHASER_NOTIFIED
                logger.info(
                    f"Voucher purchased notification email sent for voucher {self.voucher_number}",
                )
            except SendVoucherRecipientEmailNotificationFailed(
                error_message.format(self.id, timezone.now(), e)
            ) as e:
                self.processing_status = Voucher.NOT_DELIVERED_TO_PURCHASER
                logger.exception(error_message.format(self.id, timezone.now(), e))

    def send_voucher_sent_notification_emails(self):
        error_message = "An exception occured trying to run "
        error_message += "send_voucher_purchase_notification_email for Voucher with id {} at {}. Exception {}"
        with transaction.atomic():
            try:
                VoucherEmails.send_voucher_recipient_notification_email(self)
                VoucherEmails.send_voucher_purchaser_sent_notification_email(self)
                self.processing_status = Voucher.DELIVERED_TO_RECIPIENT
                logger.info(
                    f"Voucher sent notification emails sent for voucher {self.voucher_number}",
                )
            except SendVoucherRecipientEmailNotificationFailed(
                error_message.format(self.id, timezone.now(), e)
            ) as e:
                self.processing_status = Voucher.NOT_DELIVERED_TO_RECIPIENT
                logger.exception(error_message.format(self.id, timezone.now(), e))


class VoucherTransactionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("voucher")


class VoucherTransaction(models.Model):
    objects = VoucherTransactionManager()

    voucher = models.ForeignKey(
        Voucher, related_name="transactions", on_delete=models.PROTECT
    )
    park_pass = models.OneToOneField(
        Pass,
        on_delete=models.PROTECT,
        related_name="voucher_transaction",
        null=False,
        blank=False,
    )
    credit = models.DecimalField(
        max_digits=7, decimal_places=2, blank=False, null=False
    )
    debit = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return (
            "Voucher Code "
            + self.voucher.code
            + " used to purchase Park Pass "
            + self.park_pass.pass_number
        )

    def remaining_balance_excluding_this_transaction(self):
        this_transaction_balance = self.credit - self.debit
        if Decimal(0.00) == this_transaction_balance:
            return Decimal(0.00)
        if Decimal(0.00) > this_transaction_balance:
            return self.voucher.remaining_balance - this_transaction_balance
        return self.voucher.remaining_balance + this_transaction_balance

    def balance(self):
        return self.credit - self.debit
