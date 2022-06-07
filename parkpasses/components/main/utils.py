import requests
from ledger_api_client.ledger_models import EmailUserRO
import json
import pytz
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers

from parkpasses.components.main.serializers import EmailUserROSerializerForReferral


def retrieve_department_users():
    # try:
    #     res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER, settings.LEDGER_PASS), verify=False)
    #     res.raise_for_status()
    #     cache.set('department_users', json.loads(res.content).get('objects'), 10800)
    # except:
    #     raise
    dep_users = (
        EmailUserRO.objects.filter(Q(email__endswith="@dbca.wa.gov.au"))
        .exclude(Q(first_name=""), Q(last_name=""))
        .order_by("first_name")
    )
    serialiser = EmailUserROSerializerForReferral(dep_users, many=True)
    return serialiser.data


def handle_validation_error(e):
    # if hasattr(e, 'error_dict'):
    #     raise serializers.ValidationError(repr(e.error_dict))
    # else:
    #     raise serializers.ValidationError(repr(e[0].encode('utf-8')))
    if hasattr(e, "error_dict"):
        raise serializers.ValidationError(repr(e.error_dict))
    else:
        if hasattr(e, "message"):
            raise serializers.ValidationError(e.message)
        else:
            raise


def get_department_user(email):
    try:
        res = requests.get(
            "{}/api/users?email={}".format(settings.CMS_URL, email),
            auth=(settings.LEDGER_USER, settings.LEDGER_PASS),
            verify=False,
        )
        res.raise_for_status()
        data = json.loads(res.content).get("objects")
        if len(data) > 0:
            return data[0]
        else:
            return None
    except:
        raise


def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)


def check_db_connection():
    """check connection to DB exists, connect if no connection exists"""
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception as e:
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


def get_dbca_lands_and_waters_geojson():
    data = cache.get("dbca_legislated_lands_and_waters")
    if not data:
        URL = "https://kmi.dpaw.wa.gov.au/geoserver/public/ows"
        PARAMS = _get_params("public:dbca_legislated_lands_and_waters")
        res = requests.get(url=URL, params=PARAMS)
        # geo_json = res.json()
        cache.set(
            "dbca_legislated_lands_and_waters", res.json(), settings.LOV_CACHE_TIMEOUT
        )
        data = cache.get("dbca_legislated_lands_and_waters")
    # print(data.get('properties'))
    return data


def get_dbca_lands_and_waters_geos():
    geojson = get_dbca_lands_and_waters_geojson()
    geoms = []
    for feature in geojson.get("features"):
        feature_geom = feature.get("geometry")
        geos_geom = GEOSGeometry("{}".format(feature_geom)).prepared
        geoms.append(geos_geom)
    return geoms
    # geos_obj = GeometryCollection(tuple(geoms))
    # print(geos_obj.valid)
    # print(geos_obj.valid_reason)
    # return geos_obj
