from rest_framework import permissions
from Users.models import RoleEnum

class IsAdminUserRole(permissions.BasePermission):
    
    # Permission qui vérifie si l'utilisateur a le rôle ADMIN ou est superuser.
  
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or 
            getattr(request.user, 'role', None) == RoleEnum.ADMIN
        )
