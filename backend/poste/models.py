from django.db import models
from employees.models import Employe

class Poste(models.Model):

    class NiveauHierarchie(models.TextChoices):
        JUNIOR    = 'JUNIOR',    'Junior'
        CONFIRME  = 'CONFIRME',  'Confirmé'
        SENIOR    = 'SENIOR',    'Senior'
        MANAGER   = 'MANAGER',   'Manager'
        DIRECTION = 'DIRECTION', 'Direction'

    intitule  = models.CharField(max_length=150, verbose_name="Intitulé du poste")
    description  = models.TextField(blank=True,     verbose_name="Description")
    niveau_hierarchie = models.CharField( max_length=20,choices=NiveauHierarchie.choices,default=NiveauHierarchie.JUNIOR,verbose_name="Niveau")
    salaire_min  = models.FloatField(default=0, verbose_name="Salaire minimum")
    salaire_max = models.FloatField(default=0, verbose_name="Salaire maximum")
    est_actif   = models.BooleanField(default=True, verbose_name="Poste actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    employes = models.ManyToManyField(Employe,blank=True,related_name='postes',verbose_name="Employés")

    def getNombreOccupants(self):
        return self.contrats.filter(statut='ACTIF').count()

    def estVacant(self):
        return self.employes.count() == 0

    def __str__(self):
        return f"{self.intitule} ({self.niveau_hierarchie})"

    class Meta:
        verbose_name = "Poste"
        ordering     = ['intitule']






