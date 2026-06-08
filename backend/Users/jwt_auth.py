# Users/jwt_auth.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from administrateur.models import Administrateur
from employees.models import Employe
from RH.models import RH

class MultiModelJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # On extrait l'email et le rôle directement depuis le Payload du JWT
        email = validated_token.get("email")
        role = validated_token.get("role")

        if not email:
            raise AuthenticationFailed("Le token ne contient pas d'adresse email.")

        # On cherche l'utilisateur dans la table correspondante à son rôle réel
        if role == 'ADMIN':
            try:
                return Administrateur.objects.get(email=email)
            except Administrateur.DoesNotExist:
                pass
        elif role == 'RH':
            try:
                return RH.objects.get(email=email)
            except RH.DoesNotExist:
                pass
        elif role == 'EMPLOYE':
            try:
                return Employe.objects.get(email=email)
            except Employe.DoesNotExist:
                pass

        # Solution de repli si le rôle n'est pas clair
        try:
            return Administrateur.objects.get(email=email)
        except Administrateur.DoesNotExist:
            try:
                return RH.objects.get(email=email)
            except RH.DoesNotExist:
                try:
                    return Employe.objects.get(email=email)
                except Employe.DoesNotExist:
                    raise AuthenticationFailed("Utilisateur introuvable dans le système.")
