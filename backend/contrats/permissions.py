from rest_framework import permissions
from RH.models import RH
from administrateur.models import Administrateur
from employees.models import Employe

class IsRhOnlyUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return isinstance(request.user, RH)


class IsRhOrAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return isinstance(request.user, RH) or isinstance(request.user, Administrateur)
