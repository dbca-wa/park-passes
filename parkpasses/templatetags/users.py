import logging
from datetime import timedelta

import pytz
from django.conf import settings
from django.template import Library
from django.utils import timezone

from parkpasses import helpers as parkpasses_helpers
from parkpasses.components.main.models import SystemMaintenance

register = Library()


logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def is_internal(context):
    request = context["request"]
    return parkpasses_helpers.is_internal(request)


@register.simple_tag(takes_context=True)
def is_parkpasses_admin(context):
    request = context["request"]
    return parkpasses_helpers.is_parkpasses_admin(request)


@register.simple_tag(takes_context=True)
def is_parkpasses_officer(context):
    request = context["request"]
    return parkpasses_helpers.is_parkpasses_officer(request)


@register.simple_tag(takes_context=True)
def is_parkpasses_payments_officer(context):
    request = context["request"]
    return parkpasses_helpers.is_parkpasses_payments_officer(request)


@register.simple_tag(takes_context=True)
def is_parkpasses_read_only_user(context):
    request = context["request"]
    return parkpasses_helpers.is_parkpasses_read_only_user(request)


@register.simple_tag(takes_context=True)
def is_parkpasses_discount_code_percentage_user(context):
    request = context["request"]
    return parkpasses_helpers.is_parkpasses_discount_code_percentage_user(request)


@register.simple_tag(takes_context=True)
def is_retailer(context):
    request = context["request"]
    return parkpasses_helpers.is_retailer(request)


@register.simple_tag(takes_context=True)
def is_retailer_admin(context):
    return parkpasses_helpers.is_retailer_admin(context["request"])


@register.simple_tag(takes_context=True)
def is_authenticated(context):
    request = context["request"]
    return parkpasses_helpers.is_authenticated(request)


@register.simple_tag()
def system_maintenance_due():
    """Returns True (actually a time str), if within <timedelta hours> of system maintenance due datetime"""
    tz = pytz.timezone(settings.TIME_ZONE)
    now = timezone.now()  # returns UTC time
    qs = SystemMaintenance.objects.filter(start_date__gte=now - timedelta(minutes=1))
    if qs:
        obj = qs.earliest("start_date")
        if now >= obj.start_date - timedelta(
            hours=settings.SYSTEM_MAINTENANCE_WARNING
        ) and now <= obj.start_date + timedelta(minutes=1):
            # display time in local timezone
            return "{} - {} (Duration: {} mins)".format(
                obj.start_date.astimezone(tz=tz).ctime(),
                obj.end_date.astimezone(tz=tz).ctime(),
                obj.duration(),
            )
    return False


@register.simple_tag()
def system_maintenance_can_start():
    """Returns True if current datetime is within 1 minute past scheduled start_date"""
    now = timezone.now()  # returns UTC time
    qs = SystemMaintenance.objects.filter(start_date__gte=now - timedelta(minutes=1))
    if qs:
        obj = qs.earliest("start_date")
        if now >= obj.start_date and now <= obj.start_date + timedelta(minutes=1):
            return True
    return False


@register.simple_tag()
def dept_support_phone2():
    return settings.DEPT_NAME
