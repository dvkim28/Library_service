from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminAllOrIfAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
                and request.user and request.user.is_authenticated):
            return True
        return request.user and request.user.is_staff
