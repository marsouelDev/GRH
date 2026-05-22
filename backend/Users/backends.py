# Users/backends.py
from django.contrib.auth.backends import ModelBackend
from administrateur.models import Administrateur
from employees.models import Employe
# Remplacez l'import ci-dessous par le chemin exact vers votre modèle RH
from RH.models import RH 

class MultiModelAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Récupère l'identifiant (DRF envoie l'email dans le paramètre 'username')
        email = username or kwargs.get('email')
        if not email:
            return None

        # 1. Tester la connexion dans la table Administrateur
        try:
            user = Administrateur.objects.get(email=email)
            if user.check_password(password):
                return user
        except Administrateur.DoesNotExist:
            pass

        # 2. Tester la connexion dans la table Employe
        try:
            user = Employe.objects.get(email=email)
            if user.check_password(password):
                return user
        except Employe.DoesNotExist:
            pass

        # 3. Tester la connexion dans la table RH
        try:
            user = RH.objects.get(email=email)
            if user.check_password(password):
                return user
        except RH.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        # Django a besoin de récupérer l'instance de l'utilisateur actif par son ID
        # On cherche séquentiellement dans les trois tables
        try:
            return Administrateur.objects.get(pk=user_id)
        except Administrateur.DoesNotExist:
            try:
                return Employe.objects.get(pk=user_id)
            except Employe.DoesNotExist:
                try:
                    return RH.objects.get(pk=user_id)
                except RH.DoesNotExist:
                    return None