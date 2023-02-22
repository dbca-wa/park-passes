import logging

from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class LedgerAPIException(APIException):
    """Exception when there is an error accessing the ledger api"""
