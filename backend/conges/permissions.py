from rest_framework import permissions
from Users.models import RoleEnum

class IsRhUserRole(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (getattr(request.user, 'role', None) == RoleEnum.RH)
