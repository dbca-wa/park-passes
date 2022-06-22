""" Custom exceptions for the passes component """
import logging

logger = logging.getLogger(__name__)


class PassTemplateDoesNotExist(Exception):
    """The exception to be thrown if there is no pass template"""

    logger.critical(
        "CRITICAL: The system can not find a Pass Template to use for generating park passes."
    )
