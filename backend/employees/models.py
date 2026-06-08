from django.db import models
from Users.models import Utilisateur, RoleEnum


class Employe(Utilisateur):
    nom    = models.CharField(max_length=100)
    prenom  = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    telephone   = models.CharField(max_length=20, blank=True)
    salaire     = models.FloatField(default=0)
    
 
   
    def save(self, *args, **kwargs):
        self.role = RoleEnum.EMPLOYE   # toujours EMPLOYE, peu importe ce qu'on envoie
        super().save(*args, **kwargs)
 
    def seConnecter(self):
        return self.is_active
 
    def __str__(self):
        return f"{self.nom} {self.prenom}"
 
    class Meta:
        verbose_name = "Employé"