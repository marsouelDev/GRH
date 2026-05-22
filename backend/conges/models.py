from django.db import models
from employees.models import Employe

 
class Conge(models.Model):
 
    class TypeConge(models.TextChoices):
        ANNUEL = 'ANNUEL',     'Congé annuel'
        MALADIE = 'MALADIE',    'Congé maladie'
        MATERNITE = 'MATERNITE',  'Congé maternité'
        SANS_SOLDE = 'SANS_SOLDE', 'Sans solde'
        AUTRE = 'AUTRE',      'Autre'
 
    class StatutConge(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        APPROUVE = 'APPROUVE',   'Approuvé'
        REFUSE = 'REFUSE',     'Refusé'
        ANNULE = 'ANNULE',     'Annulé'
 
    employe = models.ForeignKey(Employe,on_delete=models.CASCADE,related_name='conges')
    type_conge = models.CharField(max_length=20,choices=TypeConge.choices,)
    date_debut  = models.DateField()
    date_fin  = models.DateField()
    motif   = models.TextField(blank=True)
    statut   = models.CharField(max_length=20,choices=StatutConge.choices,)
    date_demande = models.DateTimeField(auto_now_add=True)
    commentaire  = models.TextField(blank=True)  
 
    def calculerDuree(self):
        return (self.date_fin - self.date_debut).days + 1
 
    def approuver(self):
        self.statut = self.StatutConge.APPROUVE
        self.save()
 
    def refuser(self, commentaire=''):
        self.statut     = self.StatutConge.REFUSE
        self.commentaire = commentaire
        self.save()
 
    def annuler(self):
        self.statut = self.StatutConge.ANNULE
        self.save()
 
    def __str__(self):
        return f"{self.employe} — {self.type_conge} — {self.date_debut} au {self.date_fin}"
 
    class Meta:
        verbose_name = "Congé"
        ordering     = ['-date_demande']
