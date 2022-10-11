from django.conf import settings

from parkpasses.settings import template_group, template_title


def parkpasses_url(request):
    return {
        "GIT_COMMIT_DATE": settings.GIT_COMMIT_DATE,
        "GIT_COMMIT_HASH": settings.GIT_COMMIT_HASH,
        "template_group": template_group,
        "template_title": template_title,
        "build_tag": settings.BUILD_TAG,
        "LEDGER_UI_URL": settings.LEDGER_UI_URL,
        "PARKPASSES_PAYMENT_SYSTEM_PREFIX": settings.PARKPASSES_PAYMENT_SYSTEM_PREFIX,
    }
