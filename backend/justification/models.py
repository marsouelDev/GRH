from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from employees.models import Employe


class Justification(models.Model):
    class StatutJustification(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDEE    = 'VALIDEE',    'Validée'
        REJETEE    = 'REJETEE',    'Rejetée'

    class TypeJustification(models.TextChoices):
        RETARD  = 'RETARD',     'Retard'
        ABSENCE = 'ABSENCE',    'Absence'

    presence = models.OneToOneField( 'presences.Presence', on_delete=models.CASCADE, related_name='justification', verbose_name="Présence concernée")
    employe = models.ForeignKey(Employe,on_delete=models.CASCADE,related_name='justifications',verbose_name="Employé")
    type_justif = models.CharField(max_length=20,choices=TypeJustification.choices,verbose_name="Type")
    motif = models.TextField(verbose_name="Motif de la justification")
    document = models.FileField(upload_to='justifications/',null=True,blank=True,verbose_name="Document justificatif (optionnel)",help_text="PDF, JPG, PNG, DOC (max 5 Mo)")
    statut = models.CharField( max_length=20, choices=StatutJustification.choices, default=StatutJustification.EN_ATTENTE, verbose_name="Statut")
    date_soumission = models.DateTimeField(auto_now_add=True)
    commentaire_rh = models.TextField(blank=True, verbose_name="Commentaire RH")
    content_type = models.ForeignKey(ContentType,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Type de validateur")
    object_id = models.PositiveIntegerField(null=True,blank=True,verbose_name="ID du validateur")
    valide_par = GenericForeignKey('content_type', 'object_id')
    date_validation = models.DateTimeField(null=True, blank=True)

    def valider(self, rh, commentaire=''):
        from django.utils import timezone
        from django.contrib.contenttypes.models import ContentType

        self.statut = self.StatutJustification.VALIDEE
        self.commentaire_rh = commentaire
        self.date_validation = timezone.now()
        self.content_type = ContentType.objects.get_for_model(rh)
        self.object_id = rh.pk

        self.save()

    def rejeter(self, rh, commentaire=''):
        from django.utils import timezone
        from django.contrib.contenttypes.models import ContentType

        self.statut = self.StatutJustification.REJETEE
        self.commentaire_rh = commentaire
        self.date_validation = timezone.now()
        self.content_type = ContentType.objects.get_for_model(rh)
        self.object_id = rh.pk

        self.save()

    def get_valide_par_nom(self):
        if self.valide_par:
            nom = getattr(self.valide_par, 'nom', '')
            prenom = getattr(self.valide_par, 'prenom', '')
            return f"{nom} {prenom}".strip()
        return None

    def __str__(self):
        return f"Justification {self.type_justif} — {self.employe} — {self.date_soumission.date()}"

    class Meta:
        verbose_name = "Justification"
        ordering = ['-date_soumission']