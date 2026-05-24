from rest_framework import permissions

def get_role_str(user):
    user_role = getattr(user, 'role', None)
    return user_role.value if hasattr(user_role, 'value') else str(user_role)


class IsRhOnlyRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_role_str(request.user) == 'RH'


class IsRhOrAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_role_str(request.user) in ['RH', 'ADMIN']
