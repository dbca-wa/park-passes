import logging

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.managed_models import SystemGroup, SystemGroupPermission

from parkpasses.components.retailers.models import RetailerGroup, RetailerGroupUser
from parkpasses.settings import GROUP_NAME_PARK_PASSES_RETAILER

logger = logging.getLogger(__name__)


def belongs_to(request, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    if not request.user.is_authenticated:
        return False

    user = request.user

    belongs_to_value = cache.get(
        "User-belongs_to" + str(user.id) + "group_name:" + group_name
    )
    # belongs_to_value = None
    if belongs_to_value:
        print(
            "From Cache - User-belongs_to" + str(user.id) + "group_name:" + group_name
        )
    if belongs_to_value is None:
        sg = SystemGroup.objects.filter(name=group_name)
        if sg.count() > 0:
            sgp = SystemGroupPermission.objects.filter(
                system_group=sg[0], emailuser=user
            )
            if sgp.count() > 0:
                belongs_to_value = True
            # belongs_to_value = SystemGroup.object.filter(name=group_name).exists()
        cache.set(
            "User-belongs_to" + str(user.id) + "group_name:" + group_name,
            belongs_to_value,
            3600,
        )
    return belongs_to_value


def is_parkpasses_admin(request):
    # logger.info('settings.ADMIN_GROUP: {}'.format(settings.ADMIN_GROUP))
    return request.user.is_authenticated and (
        request.user.is_superuser or belongs_to(request, settings.ADMIN_GROUP)
    )


def is_retailer(request):
    if not request.user.is_authenticated:
        return False

    user = request.user
    try:
        system_group = SystemGroup.objects.get(name=GROUP_NAME_PARK_PASSES_RETAILER)
        in_retailer_group = RetailerGroupUser.objects.filter(
            emailuser_id=user.id
        ).count()
        if user.id not in system_group.get_system_group_member_ids():
            return False
        if in_retailer_group:
            return True

    except ObjectDoesNotExist:
        logger.critical(
            f"The group {GROUP_NAME_PARK_PASSES_RETAILER} named in setting\
                 GROUP_NAME_PARK_PASSES_RETAILER does not exist."
        )
        return False


def get_retailer_groups_for_user(request):
    if not request.user.is_authenticated:
        return False
    if not is_retailer(request):
        return False

    retailer_group_ids = list(
        RetailerGroupUser.objects.filter(email_user=request.user)
        .values_list("retailer_group__id", flat=True)
        .order_by("id")
    )

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
