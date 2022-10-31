import pytz
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from org_model_logs.models import CommunicationsLogEntry, EntryType


def handle_validation_error(e):
    if hasattr(e, "error_dict"):
        raise serializers.ValidationError(repr(e.error_dict))
    else:
        if hasattr(e, "message"):
            raise serializers.ValidationError(e.message)
        else:
            raise


def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)


def check_db_connection():
    """check connection to DB exists, connect if no connection exists"""
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception:
        connection.connect()


def _get_params(layer_name):
    return {
        "SERVICE": "WFS",
        "VERSION": "1.0.0",
        "REQUEST": "GetFeature",
        "typeName": layer_name,
        "maxFeatures": 50000,
        "outputFormat": "application/json",
    }


def log_communication(to, message, entry_type, instance):
    content_type = ContentType.objects.get_for_model(instance)
    entry_type = EntryType.objects.get(entry_type__iexact=entry_type)
    staff = EmailUser.objects.get(email__icontains=settings.DEFAULT_FROM_EMAIL)
    communication_log_kwargs = {
        "content_type": content_type,
        "object_id": str(instance.id),
        "to": to,
        "fromm": settings.DEFAULT_FROM_EMAIL,
        "entry_type": entry_type,
        "subject": message.subject,
        "text": message.body,
        "customer": instance.user,
        "staff": staff.id,
    }
    CommunicationsLogEntry.objects.log_communication(**communication_log_kwargs)
