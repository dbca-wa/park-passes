import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.managed_models import SystemGroupPermission

from parkpasses.components.retailers.models import RetailerGroup, RetailerGroupUser

logger = logging.getLogger(__name__)


def belongs_to(request, group_name):
    if not request.user.is_authenticated:
        return False

    user = request.user
    cache_key = "user-" + str(user.id) + "-is-a-member-of-" + slugify(group_name)
    belongs_to_value = cache.get(cache_key)
    if belongs_to_value is None:
        belongs_to_value = SystemGroupPermission.objects.filter(
            system_group__name=group_name, emailuser=user
        ).exists()
        cache.set(cache_key, belongs_to_value, 3600)
    return belongs_to_value


def is_parkpasses_admin(request):
    if not request.user.is_authenticated:
        return False
    cache_key = (
        "user-"
        + str(request.user.id)
        + "-is-a-member-of-"
        + slugify(settings.ADMIN_GROUP)
    )
    is_parkpasses_admin = cache.get(cache_key)
    if is_parkpasses_admin is None:
        is_parkpasses_admin = request.user.is_superuser or belongs_to(
            request, settings.ADMIN_GROUP
        )
        cache.set(cache_key, is_parkpasses_admin, 3600)
    return is_parkpasses_admin


def is_retailer(request):
    if not request.user.is_authenticated:
        return False

    cache_key = "user-" + str(request.user.id) + "-is-a-retailer"
    is_retailer = cache.get(cache_key)
    logger.debug("is_retailer = " + str(is_retailer))
    if is_retailer is None:
        is_retailer = RetailerGroupUser.objects.filter(
            active=True, retailer_group__active=True, emailuser_id=request.user.id
        ).exists()
        cache.set(cache_key, is_retailer, 3600)
    return is_retailer


def is_retailer_admin(request):
    if not is_retailer(request):
        return False

    cache_key = "user-" + str(request.user.id) + "-is-a-retailer-admin"
    is_retailer_admin = cache.get(cache_key)
    logger.debug("is_retailer_admin = " + str(is_retailer))
    if is_retailer_admin is None:
        is_retailer_admin = RetailerGroupUser.objects.filter(
            active=True,
            retailer_group__active=True,
            is_admin=True,
            emailuser_id=request.user.id,
        ).exists()
        cache.set(cache_key, is_retailer_admin, 3600)
    return is_retailer_admin


def get_retailer_group_ids_for_user(request):
    return list(
        RetailerGroupUser.objects.filter(emailuser=request.user)
        .values_list("retailer_group__id", flat=True)
        .order_by("id")
    )


def get_retailer_groups_for_user(request):
    if not request.user.is_authenticated:
        return False
    if not is_retailer(request):
        return False

    retailer_group_ids = get_retailer_group_ids_for_user(request)

    return RetailerGroup.objects.filter(id__in=retailer_group_ids)


def in_dbca_domain(request):
    return request.user.is_staff


def is_in_organisation_contacts(request, organisation):
    return request.user.email in organisation.contacts.all().values_list(
        "email", flat=True
    )


def is_departmentUser(request):
    return request.user.is_authenticated and request.user.is_staff


def is_customer(request):
    return request.user.is_authenticated and not request.user.is_staff


def is_authenticated(request):
    return request.user.is_authenticated


def is_internal(request):
    return is_departmentUser(request)


def get_all_officers():
    return EmailUser.objects.filter(groups__name="Commercial Operator Admin")
