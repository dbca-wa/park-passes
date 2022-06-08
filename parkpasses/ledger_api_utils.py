import logging

from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.main.decorators import basic_exception_handler

logger = logging.getLogger("parkpasses")


@basic_exception_handler
def retrieve_email_user(email_user_id):
    return EmailUser.objects.get(id=email_user_id)
