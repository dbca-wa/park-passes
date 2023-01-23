import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.managed_models import SystemGroupPermission

from parkpasses.components.passes.models import Pass
from parkpasses.components.retailers.models import RetailerGroup, RetailerGroupUser

logger = logging.getLogger(__name__)


def belongs_to(request, group_name):
    if not request.user.is_authenticated:
        return False
    if request.user.is_superuser:
        return True

    user = request.user
    cache_key = settings.CACHE_KEY_BELONGS_TO.format(str(user.id), slugify(group_name))
    belongs_to_value = cache.get(cache_key)
    if belongs_to_value is None:
        belongs_to_value = SystemGroupPermission.objects.filter(
            system_group__name=group_name, emailuser=user, active=True
        ).exists()
        cache.set(cache_key, belongs_to_value, settings.CACHE_TIMEOUT_2_HOURS)
    return belongs_to_value


def is_internal(request):
    if not request.user.is_authenticated:
        return False
    if request.user.is_superuser:
        return True

    user = request.user
    cache_key = settings.CACHE_KEY_IS_INTERNAL.format(str(user.id))
    is_internal = cache.get(cache_key)
    if is_internal is None:
        is_internal = (
            is_parkpasses_admin(request)
            or is_parkpasses_officer(request)
            or is_parkpasses_payments_officer(request)
            or is_parkpasses_read_only_user(request)
            or is_parkpasses_discount_code_percentage_user(request)
        )
        cache.set(cache_key, is_internal, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{is_internal}")
    return is_internal


def test_async(var):
    print("var = " + str(var))


def generate_park_pass_pdf_from_id(id):
    park_pass = Pass.objects.get(id=id)
    park_pass.generate_park_pass_pdf()
    park_pass.update()


def is_parkpasses_admin(request):
    return belongs_to(request, settings.ADMIN_GROUP)


def is_parkpasses_officer(request):
    return belongs_to(request, settings.OFFICER_GROUP)


def is_parkpasses_payments_officer(request):
    return belongs_to(request, settings.PAYMENTS_OFFICER_GROUP)


def is_parkpasses_read_only_user(request):
    return belongs_to(request, settings.READ_ONLY_GROUP)


def is_parkpasses_discount_code_percentage_user(request):
    return belongs_to(request, settings.DISCOUNT_CODE_PERCENTAGE_GROUP)


def is_retailer(request):
    if not request.user.is_authenticated:
        return False

    cache_key = settings.CACHE_KEY_RETAILER.format(str(request.user.id))
    is_retailer = cache.get(cache_key)
    if is_retailer is None:
        is_retailer = RetailerGroupUser.objects.filter(
            active=True, retailer_group__active=True, emailuser_id=request.user.id
        ).exists()
        cache.set(cache_key, is_retailer, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{is_retailer}")
    return is_retailer


def is_retailer_admin(request):
    if not is_retailer(request):
        return False
    if request.user.is_superuser:
        return True

    cache_key = settings.CACHE_KEY_RETAILER_ADMIN.format(str(request.user.id))
    is_retailer_admin = cache.get(cache_key)
    if is_retailer_admin is None:
        is_retailer_admin = RetailerGroupUser.objects.filter(
            active=True,
            retailer_group__active=True,
            is_admin=True,
            emailuser_id=request.user.id,
        ).exists()
        cache.set(cache_key, is_retailer_admin, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{is_retailer_admin}")
    return is_retailer_admin


def get_retailer_group_ids_for_user(request):
    cache_key = settings.CACHE_KEY_RETAILER_GROUP_IDS.format(str(request.user.id))
    retailer_group_ids = cache.get(cache_key)
    if retailer_group_ids is None:
        retailer_group_ids = list(
            RetailerGroupUser.objects.filter(emailuser=request.user)
            .values_list("retailer_group__id", flat=True)
            .order_by("id")
        )
        cache.set(cache_key, retailer_group_ids, settings.CACHE_TIMEOUT_2_HOURS)
    logger.debug(f"{cache_key}:{retailer_group_ids}")
    return retailer_group_ids


def get_retailer_groups_for_user(request):
    if not request.user.is_authenticated:
        return False
    if not is_retailer(request):
        return False

    retailer_group_ids = get_retailer_group_ids_for_user(request)

    return RetailerGroup.objects.filter(id__in=retailer_group_ids)


def get_rac_discount_code(email):
    discount_hash = hashlib.shake_256(
        (settings.RAC_HASH_SALT + email).encode("utf-8")
    ).hexdigest(10)
    return discount_hash


def check_rac_discount_hash(discount_hash, email):
    return discount_hash == hashlib.shake_256(
        (settings.RAC_HASH_SALT + email).encode("utf-8")
    ).hexdigest(10)


def in_dbca_domain(request):
    return request.user.is_staff


def is_in_organisation_contacts(request, organisation):
    return request.user.email in organisation.contacts.all().values_list(
        "email", flat=True
    )


def is_departmentUser(request):
    return request.user.is_authenticated and request.user.is_staff


def is_customer(request):
    if is_retailer(request):
        return False
    return request.user.is_authenticated and not request.user.is_staff


def is_authenticated(request):
    return request.user.is_authenticated


def get_all_officers():
    return EmailUser.objects.filter(groups__name="Commercial Operator Admin")
