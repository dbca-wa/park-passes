from rest_framework.permissions import BasePermission

from parkpasses.helpers import is_internal, is_retailer


class IsInternal(BasePermission):
    def has_permission(self, request, view):
        return is_internal(request)


class IsRetailer(BasePermission):
    def has_permission(self, request, view):
        return is_retailer(request)
