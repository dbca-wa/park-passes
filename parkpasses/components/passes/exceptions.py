""" Custom exceptions for the passes component """
import logging

logger = logging.getLogger(__name__)


class PassTemplateDoesNotExist(Exception):
    """The exception to be raised if there is no pass template"""


class MultipleDefaultPricingWindowsExist(Exception):
    """The exception to be thrown if there is more than one default pricing window for pass type"""


class NoDefaultPricingWindowExists(Exception):
    """The exception to be thrown if there is no default pricing window for pass type"""
