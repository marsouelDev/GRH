# administrateur/permissions.py
from rest_framework import permissions
from Users.models import RoleEnum

# Assurez-vous que ce nom correspond exactement à l'import
class IsAdminUserRole(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        user_role = getattr(request.user, 'role', None)
        role_value = user_role.value if hasattr(user_role, 'value') else str(user_role)
        
        return (
            request.user.is_superuser or 
            role_value in ['ADMIN', RoleEnum.ADMIN]
        )
