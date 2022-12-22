""" Custom exceptions for the retailers component """
import logging

logger = logging.getLogger(__name__)


class MultipleDBCARetailerGroupsExist(Exception):
    """The exception to be thrown if there is more than one retailer group containing 'DBCA'"""


class NoDBCARetailerGroupExists(Exception):
    """The exception to be thrown if there is no retailer group containing 'DBCA'"""


class MultipleRACRetailerGroupsExist(Exception):
    """The exception to be thrown if there is more than one retailer group containing 'RAC'"""


class NoRACRetailerGroupExists(Exception):
    """The exception to be thrown if there is no retailer group containing 'RAC'"""
