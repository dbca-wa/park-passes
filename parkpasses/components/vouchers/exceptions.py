""" Custom exceptions for the vouchers component """
import logging

logger = logging.getLogger(__name__)


class RemainingBalanceExceedsVoucherAmountException(Exception):
    """The exception to be raised if the total value of voucher transactions is
    greater than the total amount of the voucher"""


class RemainingVoucherBalanceLessThanZeroException(Exception):
    """The exception to be thrown if the remaining balance of a voucher is less than zero"""


class SendVoucherRecipientEmailNotificationFailed(Exception):
    """The exeption to be thrown if any exceptions occur during the send_voucher_email method."""


class RetailerGroupUsersCannotPurchaseGiftVouchers(Exception):
    """The exception to be thrown if a retailer group user attempts to purchase a gift voucher"""
