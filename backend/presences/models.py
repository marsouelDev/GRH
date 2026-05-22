from django.db import models
from employees.models import Employe

class Presence(models.Model):

    class Statut(models.TextChoices):
        PRESENT = 'PRESENT', 'Présent'
        ABSENT  = 'ABSENT',  'Absent'
        RETARD  = 'RETARD',  'En retard'

    employe  = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='presences')
    
  
    date   = models.DateField(auto_now_add=True)
    
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart  = models.TimeField(null=True, blank=True)
    statut   = models.CharField(max_length=10, choices=Statut.choices)
    

    def calculerHeures(self):
        if self.heure_arrivee and self.heure_depart:
            from datetime import datetime, date
            debut = datetime.combine(date.today(), self.heure_arrivee)
            fin   = datetime.combine(date.today(), self.heure_depart)
            return round((fin - debut).seconds / 3600, 2)
        return 0.0

    def __str__(self):
        return f"{self.employe} — {self.date} — {self.statut}"

    class Meta:
        verbose_name    = "Présence"
        unique_together = ('employe', 'date')
        ordering        = ['-date']


