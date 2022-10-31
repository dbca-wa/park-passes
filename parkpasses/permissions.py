import logging

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework_api_key.permissions import BaseHasAPIKey

from parkpasses.components.retailers.models import RetailerGroupAPIKey
from parkpasses.helpers import (
    get_retailer_group_ids_for_user,
    is_internal,
    is_parkpasses_officer,
    is_parkpasses_payments_officer,
    is_retailer,
    is_retailer_admin,
)

logger = logging.getLogger(__name__)


class IsInternal(BasePermission):
    def has_permission(self, request, view):
        logger.debug("request.user.is_superuser = " + str(request.user.is_superuser))
        if is_internal(request):
            if view.action in ["destroy"]:
                return False
            if view.action in ["retrieve", "list"]:
                return True
            if (
                request.user.is_superuser
                or is_parkpasses_payments_officer(request)
                or is_parkpasses_officer(request)
            ):
                return True
        return False


class IsInternalAPIView(BasePermission):
    def has_permission(self, request, view):
        if is_internal(request):
            if "DELETE" == request.method:
                return False

            return True
        return False


class IsInternalOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or is_internal(request))


class IsRetailer(BasePermission):
    def has_permission(self, request, view):
        return is_retailer(request)


class IsRetailerAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_retailer_admin(request)


class IsRetailerObjectCreator(BasePermission):
    def has_permission(self, request, view):
        return is_retailer(request)

    def has_object_permission(self, request, view, obj):
        return obj.sold_via in get_retailer_group_ids_for_user(request)


class IsExternalObjectOwner(BasePermission):
    """This permission will only work with objects where the email user id field is called user"""

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user


class HasRetailerGroupAPIKey(BaseHasAPIKey):
    model = RetailerGroupAPIKey

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return super().has_object_permission(request, view, obj)
