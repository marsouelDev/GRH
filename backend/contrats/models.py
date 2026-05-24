from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from employees.models import Employe
from poste.models import Poste

class Contrat(models.Model):
    class TYPE_CONTRAT(models.TextChoices):
        CDI = 'CDI', 'Contrat à Durée Indéterminée'
        CDD = 'CDD', 'Contrat à Durée Déterminée'
        STAGE = 'STAGE', 'Stage'
        FREELANCE = 'FREELANCE', 'Prestation Freelance'
    
    class STATUT_CONTRAT(models.TextChoices):
        ACTIF = 'ACTIF', 'En cours'
        TERMINE = 'TERMINE', 'Terminé'
        SUSPENDU = 'SUSPENDU', 'Suspendu'
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='contrats',verbose_name="Employé")
    type_contrat = models.CharField(max_length=15, choices=TYPE_CONTRAT.choices, default='CDI',verbose_name="Type de contrat")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],verbose_name="Salaire de base")
    statut = models.CharField(max_length=15, choices=STATUT_CONTRAT.choices,  default='ACTIF',verbose_name="Statut")
    poste = models.ForeignKey(Poste,on_delete=models.PROTECT,  related_name='contrats',verbose_name="Poste")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de saisie")

    def clean(self):
        super().clean()
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError({'date_fin': "La date de fin ne peut pas précéder la date de début."})
        if self.type_contrat in ['CDD', 'STAGE'] and not self.date_fin:
            raise ValidationError({'date_fin': f"Une date de fin est obligatoire pour les contrats de type {self.type_contrat}."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contrat {self.type_contrat} - {self.employe.nom} ({self.poste.intitule})"
