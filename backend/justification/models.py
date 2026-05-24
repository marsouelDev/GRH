from django.db import models
from employees.models import Employe
class Justification(models.Model):
    class StatutJustification(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDEE  = 'VALIDEE',    'Validée'
        REJETEE  = 'REJETEE',    'Rejetée'

    class TypeJustification(models.TextChoices):
        RETARD  = 'RETARD',     'Retard'
        ABSENCE = 'ABSENCE',    'Absence'

   
    presence  = models.OneToOneField('presences.Presence',on_delete=models.CASCADE,related_name='justification',verbose_name="Présence concernée")
    employe = models.ForeignKey(Employe,on_delete=models.CASCADE,related_name='justifications',verbose_name="Employé")
    type_justif = models.CharField(max_length=20,choices=TypeJustification.choices,verbose_name="Type")
    motif = models.TextField(verbose_name="Motif de la justification")
    document = models.FileField(upload_to='justifications/',null=True, blank=True,verbose_name="Document justificatif (optionnel)")
    statut  = models.CharField(max_length=20,choices=StatutJustification.choices,default=StatutJustification.EN_ATTENTE,verbose_name="Statut")
    date_soumission = models.DateTimeField(auto_now_add=True)
    commentaire_rh  = models.TextField(blank=True, verbose_name="Commentaire RH")
    valide_par      = models.ForeignKey(Employe,on_delete=models.SET_NULL,null=True, blank=True,related_name='justifications_validees',verbose_name="Validé par")
    date_validation = models.DateTimeField(null=True, blank=True)

    def valider(self, rh, commentaire=''):
        from django.utils import timezone
        self.statut          = self.StatutJustification.VALIDEE
        self.valide_par      = rh
        self.commentaire_rh  = commentaire
        self.date_validation = timezone.now()
        self.save()

    def rejeter(self, rh, commentaire=''):
        from django.utils import timezone
        self.statut          = self.StatutJustification.REJETEE
        self.valide_par      = rh
        self.commentaire_rh  = commentaire
        self.date_validation = timezone.now()
        self.save()

    def __str__(self):
        return f"Justification {self.type_justif} — {self.employe} — {self.date_soumission.date()}"

    class Meta:
        verbose_name = "Justification"
        ordering     = ['-date_soumission']
