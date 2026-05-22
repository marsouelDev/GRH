from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from administrateur.models import Administrateur
from employees.models import Employe
from RH.models import RH
class MultiModelJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            raise InvalidToken("Token contient pas d'identifiant utilisateur")
        # Chercher dans les 3 tables
        for Model in [Administrateur, Employe, RH]:
            try:
                user = Model.objects.get(pk=user_id)
                if not user.is_active:
                    raise InvalidToken("Utilisateur inactif")
                return user
            except Model.DoesNotExist:
                continue
        raise InvalidToken("Utilisateur introuvable")  