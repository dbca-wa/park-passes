from rest_framework.permissions import SAFE_METHODS, BasePermission

from parkpasses.helpers import is_internal, is_retailer, is_retailer_admin


class IsInternal(BasePermission):
    def has_permission(self, request, view):
        return is_internal(request)


class IsInternalOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or request.user and is_internal(request)
        )


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
