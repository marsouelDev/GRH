from rest_framework import permissions

def get_user_role(request) -> str:
    if not request.user or not request.user.is_authenticated:
        return ''
    
    if hasattr(request, 'auth') and request.auth and 'role' in request.auth:
        return str(request.auth['role'])

    role = getattr(request.user, 'role', None)
    if role is None:
        return ''
    return role.value if hasattr(role, 'value') else str(role)


class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request)
        if role != 'ADMIN':
            return False
        return request.method in permissions.SAFE_METHODS


class IsRhUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request) == 'RH'


class IsEmployeUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request) == 'EMPLOYE'

    def has_object_permission(self, request, view, obj):
        return obj.employe == request.user
