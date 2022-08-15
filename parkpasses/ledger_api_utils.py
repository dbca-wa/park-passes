import logging

from django.core.cache import cache
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.main.decorators import basic_exception_handler

logger = logging.getLogger(__name__)


@basic_exception_handler
def retrieve_email_user(email_user_id):
    emailuser = cache.get("email_user_" + str(email_user_id))
    if emailuser is None:
        emailuser = EmailUser.objects.get(id=email_user_id)
        cache.set("email_user_" + str(email_user_id), emailuser, 300)
        return emailuser
    return emailuser
