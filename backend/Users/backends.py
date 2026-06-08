# Users/backends.py
from django.contrib.auth.backends import ModelBackend
from administrateur.models import Administrateur
from employees.models import Employe
from RH.models import RH 

class MultiModelAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username or kwargs.get('email')
        if not email:
            return None

        # 1. Administrateur
        try:
            user = Administrateur.objects.get(email=email)
            if user.check_password(password):
                return user
        except Administrateur.DoesNotExist:
            pass

        # 2. Employe
        try:
            user = Employe.objects.get(email=email)
            if user.check_password(password):
                return user
        except Employe.DoesNotExist:
            pass

        # 3. RH
        try:
            user = RH.objects.get(email=email)
            if user.check_password(password):
                return user
        except RH.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        # Sécurité : Si l'ID correspond à un Admin d'abord (car AUTH_USER_MODEL point sur lui)
        try:
            return Administrateur.objects.get(pk=user_id)
        except Administrateur.DoesNotExist:
            pass
        
        try:
            return Employe.objects.get(pk=user_id)
        except Employe.DoesNotExist:
            pass
            
        try:
            return RH.objects.get(pk=user_id)
        except RH.DoesNotExist:
            return None
