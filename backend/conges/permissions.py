from rest_framework import permissions

def get_user_role(request):
    """Fonction utilitaire pour extraire le rôle au format texte brut."""
    if not request.user or not request.user.is_authenticated:
        return None
    user_role = getattr(request.user, 'role', None)
    return user_role.value if hasattr(user_role, 'value') else str(user_role)


class IsAdminUserRole(permissions.BasePermission):
  
    def has_permission(self, request, view):
        role = get_user_role(request)
        if role == 'ADMIN' and request.method in permissions.SAFE_METHODS: 
            return True
        return False


class IsRhUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request) == 'RH'


class IsEmployeUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request)
        return role == 'EMPLOYE'

    def has_object_permission(self, request, view, obj):
        return obj.employe == request.user
