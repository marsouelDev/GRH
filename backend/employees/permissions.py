from rest_framework import permissions
from Users.models import RoleEnum
from rest_framework.response import Response
from rest_framework import status

class IsRhOrAdmin(permissions.BasePermission):
    def has_persmission_and_role(self,request,view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = getattr(request,'role',None) #Récupération sécurisée du rôle affecté au compte utilisateur
        autorise = user_role in [RoleEnum.RH, RoleEnum.ADMIN]
        return Response({
            "can_create": autorise,
            "current_role": user_role,
            "allowed_roles": [RoleEnum.RH, RoleEnum.ADMIN]
        }, status=status.HTTP_200_OK)
        