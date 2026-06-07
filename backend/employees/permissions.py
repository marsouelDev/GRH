from rest_framework import permissions
from Users.models import RoleEnum

class IsRhOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False  
            
        user_role = getattr(request.user, 'role', None)
        
        allowed_roles = [
            RoleEnum.RH, RoleEnum.RH.value, "RH",
            RoleEnum.ADMIN, RoleEnum.ADMIN.value, "ADMIN"
        ]
        
        return request.user.is_superuser or user_role in allowed_roles