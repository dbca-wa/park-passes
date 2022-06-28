from rest_framework.permissions import BasePermission

from parkpasses.helpers import is_internal


class IsInternal(BasePermission):
    def has_permission(self, request, view):
        return is_internal(request)
