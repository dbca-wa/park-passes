from django.conf import settings
from django.template import Library

register = Library()


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


@register.filter
def total_line_price(price, qty):
    return f"{round(price * qty, 2):.2f}"


@register.filter
def basket_total_price(lines):
    total = 0.00
    for line in lines:
        total += line["price_incl_tax"] * line["quantity"]
    return f"{round(total, 2):.2f}"


@register.simple_tag()
def build_tag():
    return settings.BUILD_TAG
