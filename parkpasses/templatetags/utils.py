from django.conf import settings
from django.template import Library

from parkpasses.helpers import park_passes_system_check

register = Library()


@register.simple_tag()
def system_check():
    messages = []
    critical_issues = []
    passed = False
    park_passes_system_check(messages, critical_issues)
    if len(critical_issues) == 0:
        passed = True
    return {"passed": passed, "messages": messages, "critical_issues": critical_issues}


@register.simple_tag()
def system_name():
    return settings.SYSTEM_NAME


@register.simple_tag()
def system_name_short():
    return settings.SYSTEM_NAME_SHORT


@register.simple_tag()
def support_email():
    return settings.SUPPORT_EMAIL


@register.simple_tag()
def dept_name():
    return settings.DEP_NAME


@register.simple_tag()
def dept_support_phone():
    return settings.DEP_PHONE_SUPPORT


@register.simple_tag()
def can_show_tests():
    return settings.SHOW_TESTS_URL


@register.simple_tag()
def build_tag():
    return settings.BUILD_TAG
