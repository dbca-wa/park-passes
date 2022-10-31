""" Custom exceptions for the cart component """
import logging

logger = logging.getLogger(__name__)


class CartUserDoesNotExist(Exception):
    """The exception to be thrown if the user assigned to a cart doesn't exist"""


class CartItemContainsInvalidObjectId(Exception):
    """The exception to be thrown if the object attached to a cart item doesn't exist"""
