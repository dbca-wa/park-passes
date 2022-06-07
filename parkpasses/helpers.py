from __future__ import unicode_literals
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, EmailUserRO
from ledger_api_client.managed_models import SystemGroup
from django.conf import settings
from django.core.cache import cache

import logging

from parkpasses.settings import GROUP_NAME_ASSESSOR, GROUP_NAME_APPROVER

logger = logging.getLogger(__name__)


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    # import ipdb; ipdb.set_trace()
    belongs_to_value = cache.get(
        "User-belongs_to" + str(user.id) + "group_name:" + group_name
    )
    if belongs_to_value:
        print(
            "From Cache - User-belongs_to" + str(user.id) + "group_name:" + group_name
        )
    if belongs_to_value is None:
        belongs_to_value = user.groups().filter(name=group_name).exists()
        cache.set(
            "User-belongs_to" + str(user.id) + "group_name:" + group_name,
            belongs_to_value,
            3600,
        )
    return belongs_to_value

    # return user.groups.filter(name=group_name).exists()


# def is_model_backend(request):
#    # Return True if user logged in via single sign-on (i.e. an internal)
#    return 'ModelBackend' in request.session.get('_auth_user_backend')
#
# def is_email_auth_backend(request):
#    # Return True if user logged in via social_auth (i.e. an external user signing in with a login-token)
#    return 'EmailAuth' in request.session.get('_auth_user_backend')


def is_parkpasses_admin(request):
    # logger.info('settings.ADMIN_GROUP: {}'.format(settings.ADMIN_GROUP))
    return request.user.is_authenticated and (
        request.user.is_superuser or belongs_to(request.user, settings.ADMIN_GROUP)
    )


def is_assessor(user_id):
    if isinstance(user_id, EmailUser) or isinstance(user_id, EmailUserRO):
        user_id = user_id.id
    assessor_group = SystemGroup.objects.get(name=GROUP_NAME_ASSESSOR)
    return True if user_id in assessor_group.get_system_group_member_ids() else False


def is_approver(user_id):
    if isinstance(user_id, EmailUser) or isinstance(user_id, EmailUserRO):
        user_id = user_id.id
    assessor_group = SystemGroup.objects.get(name=GROUP_NAME_APPROVER)
    return True if user_id in assessor_group.get_system_group_member_ids() else False


def in_dbca_domain(request):
    return request.user.is_staff


#    #import ipdb; ipdb.set_trace()
#    user = request.user
#    domain = user.email.split('@')[1]
#    if domain in settings.DEPT_DOMAINS:
#        if not user.is_staff:
#            # hack to reset department user to is_staff==True, if the user logged in externally (external departmentUser login defaults to is_staff=False)
#            user.is_staff = True
#            user.save()
#        return True
#    return False


def is_in_organisation_contacts(request, organisation):
    return request.user.email in organisation.contacts.all().values_list(
        "email", flat=True
    )


def is_departmentUser(request):
    # return request.user.is_authenticated and is_model_backend(request) and in_dbca_domain(request)
    return request.user.is_authenticated and request.user.is_staff


def is_customer(request):
    # return request.user.is_authenticated and is_email_auth_backend(request)
    return request.user.is_authenticated and not request.user.is_staff


def is_internal(request):
    return is_departmentUser(request)


def get_all_officers():
    return EmailUser.objects.filter(groups__name="Commercial Operator Admin")
