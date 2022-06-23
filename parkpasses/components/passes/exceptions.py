""" Custom exceptions for the passes component """
import logging

logger = logging.getLogger(__name__)


class PassTemplateDoesNotExist(Exception):
    """The exception to be thrown if there is no pass template"""
