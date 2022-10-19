from rest_framework.permissions import SAFE_METHODS, BasePermission

from parkpasses.helpers import (
    is_internal,
    is_parkpasses_officer,
    is_parkpasses_payments_officer,
    is_retailer,
    is_retailer_admin,
)


class IsInternal(BasePermission):
    def has_permission(self, request, view):
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


class IsInternalOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or is_internal(request))


class IsRetailer(BasePermission):
    def has_permission(self, request, view):
        if is_internal(request):
            return True
        return is_retailer(request)


class IsRetailerAdmin(BasePermission):
    def has_permission(self, request, view):
        if is_internal(request):
            return True
        return is_retailer_admin(request)
