from django.db import models
from Users.models import Utilisateur, RoleEnum


class Employe(Utilisateur):

    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    salaire = models.FloatField()
    
    def seConnecter(self):

        return f"{self.email} connecté comme Employé"

    def save(self, *args, **kwargs):

        self.role = RoleEnum.EMPLOYE

        super().save(*args, **kwargs)

    def __str__(self):

        return self.email