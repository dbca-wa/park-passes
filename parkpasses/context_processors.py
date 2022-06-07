from confy import env
from django.conf import settings

# from ledger.payments.helpers import is_payment_admin

from parkpasses.settings import (
    KMI_SERVER_URL,
    template_group,
    template_title,
    BUILD_TAG,
)


def parkpasses_url(request):

    return {
        "KMI_SERVER_URL": KMI_SERVER_URL,
        "template_group": template_group,
        "template_title": template_title,
        "build_tag": BUILD_TAG,
    }
