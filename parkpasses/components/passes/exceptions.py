""" Custom exceptions for the passes component """
import logging

from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class PassTemplateDoesNotExist(Exception):
    """The exception to be raised if there is no pass template"""


class MultipleDefaultPricingWindowsExist(Exception):
    """The exception to be thrown if there is more than one default pricing window for pass type"""


class NoDefaultPricingWindowExists(Exception):
    """The exception to be thrown if there is no default pricing window for pass type"""


class NoValidPassTypeFoundInPost(APIException):
    """The exception to be thrown if the external POST request to create a pass does not
    specify a valid pass type name"""


class SendPassAutoRenewNotificationEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass autorenew
    notification email"""


class SendPassAutoRenewSuccessNotificationEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass autorenew success
    notification email"""


class SendPassAutoRenewFailureNotificationEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass autorenew failure
    notification email"""


class SendPassFinalAutoRenewFailureNotificationEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass final autorenew failure
    notification email"""


class SendPassExpiryNotificationEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass expiry
    notification email"""


class SendPassExpiredNotificationEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass expired
    notification email"""


class SendPassPurchasedEmailNotificationFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass purchase email
    notification"""


class SendPassVehicleDetailsNotYetProvidedEmailNotificationFailed(Exception):
    """The exception to be thrown if an error occurs when sending the pass vehicle details
    not yet provided email notification"""


class SendGoldPassDetailsToPICAEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the gold pass details to
    pica email"""


class SendNoPrimaryCardForAutoRenewalEmailFailed(Exception):
    """The exception to be thrown if an error occurs when sending the no primary card for
    autorenewal email"""


class NoOracleCodeFoundForCartItem(Exception):
    """The exception to be thrown if the system can not find an oracle code for a cart item"""
