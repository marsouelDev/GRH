# notification/models.py

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    class TypeNotification(models.TextChoices):
        CONGE_SOUMIS    = 'CONGE_SOUMIS',   'Congé soumis'
        CONGE_APPROUVE  = 'CONGE_APPROUVE', 'Congé approuvé'
        CONGE_REFUSE    = 'CONGE_REFUSE',   'Congé refusé'
        JUSTIF_SOUMISE  = 'JUSTIF_SOUMISE', 'Justification soumise'
        JUSTIF_VALIDEE  = 'JUSTIF_VALIDEE', 'Justification validée'
        JUSTIF_REJETEE  = 'JUSTIF_REJETEE', 'Justification rejetée'
        JUSTIF_SUPPRIMEE = 'JUSTIF_SUPPRIMEE', 'Justification supprimée' 
        ANNIVERSAIRE    = 'ANNIVERSAIRE',   'Anniversaire'
        RAPPEL          = 'RAPPEL',         'Rappel administratif'
        SYSTEME         = 'SYSTEME',        'Message système'
        CONTRAT_EXPIRE_SOON = 'CONTRAT_EXPIRE_SOON', 'Contrat expirant bientôt'
        CONTRAT_EXPIRE      = 'CONTRAT_EXPIRE',      'Contrat expiré'
        CONTRAT_CREE        = 'CONTRAT_CREE',        'Nouveau contrat créé'
        CONTRAT_CLOTURE     = 'CONTRAT_CLOTURE',     'Contrat clôturé'

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL,   null=True, blank=True, verbose_name="Type de destinataire" )
    object_id = models.PositiveIntegerField(null=True,blank=True,verbose_name="ID du destinataire")
    destinataire = GenericForeignKey('content_type', 'object_id')
    type_notif = models.CharField( max_length=30, choices=TypeNotification.choices, verbose_name="Type" )
    titre = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    lien = models.CharField(max_length=200, blank=True, verbose_name="Lien (optionnel)")
    lu = models.BooleanField(default=False, verbose_name="Lu")
    date_envoi = models.DateTimeField(auto_now_add=True)

    def marquerLu(self):
        self.lu = True
        self.save()

    def getTypeLabel(self):
        return self.get_type_notif_display()

    @classmethod
    def envoyer(cls, destinataire, type_notif, titre, message, lien=''):
        content_type = ContentType.objects.get_for_model(destinataire)
        return cls.objects.create(
            content_type=content_type,
            object_id=destinataire.pk,
            type_notif=type_notif,
            titre=titre,
            message=message,
            lien=lien,
        )

    def __str__(self):
        return f"[{self.type_notif}] → {self.destinataire} — {self.date_envoi.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Notification"
        ordering = ['-date_envoi']