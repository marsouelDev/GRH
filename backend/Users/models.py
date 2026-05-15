from django.db import models
from django.contrib.auth.models import AbstractUser


class RoleEnum(models.TextChoices):
    EMPLOYE = "EMPLOYE", "Employé"
    RH = "RH", "Gestionnaire RH"
    ADMIN = "ADMIN", "Administrateur"
    


class Utilisateur(AbstractUser):

    username = None

    email = models.EmailField( unique=True)
    role = models.CharField(max_length=20,choices=RoleEnum.choices)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']
    class Meta:
        abstract = True

    def seConnecter(self):

        raise NotImplementedError(
            "La méthode seConnecter() doit être implémentée"
        )
    
    

