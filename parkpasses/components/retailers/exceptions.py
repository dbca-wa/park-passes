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


class RetailerGroupHasNoLedgerOrganisationAttached(Exception):
    """The exception to be thrown if there is no retailer group has a null ledger_organisation field"""


class UnableToRetrieveLedgerOrganisation(Exception):
    """The exception to be thrown if no ledger organisation can be retrieved from the ledger API"""
