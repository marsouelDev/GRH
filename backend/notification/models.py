from django.db import models

from employees.models import Employe

class Notification(models.Model):

    class TypeNotification(models.TextChoices):
        CONGE_SOUMIS    = 'CONGE_SOUMIS',   'Congé soumis'
        CONGE_APPROUVE  = 'CONGE_APPROUVE', 'Congé approuvé'
        CONGE_REFUSE    = 'CONGE_REFUSE',   'Congé refusé'
        JUSTIF_SOUMISE  = 'JUSTIF_SOUMISE', 'Justification soumise'
        JUSTIF_VALIDEE  = 'JUSTIF_VALIDEE', 'Justification validée'
        JUSTIF_REJETEE  = 'JUSTIF_REJETEE', 'Justification rejetée'
        ANNIVERSAIRE    = 'ANNIVERSAIRE',   'Anniversaire'
        RAPPEL          = 'RAPPEL',         'Rappel administratif'
        SYSTEME         = 'SYSTEME',        'Message système'

    destinataire = models.ForeignKey(Employe,on_delete=models.CASCADE,related_name='notifications',verbose_name="Destinataire")
    type_notif   = models.CharField(  max_length=30, choices=TypeNotification.choices, verbose_name="Type" )
    titre  = models.CharField(max_length=200, verbose_name="Titre")
    message   = models.TextField(verbose_name="Message")
    lien     = models.CharField(max_length=200, blank=True, verbose_name="Lien (optionnel)")
    lu = models.BooleanField(default=False, verbose_name="Lu")
    date_envoi  = models.DateTimeField(auto_now_add=True)

    def marquerLu(self):
        self.lu = True
        self.save()

    def getTypeLabel(self):
        return self.get_type_notif_display()

    @classmethod
    def envoyer(cls, destinataire, type_notif, titre, message, lien=''):
        
        return cls.objects.create(
            destinataire=destinataire,
            type_notif=type_notif,
            titre=titre,
            message=message,
            lien=lien,
        )

    def __str__(self):
        return f"[{self.type_notif}] → {self.destinataire} — {self.date_envoi.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Notification"
        ordering     = ['-date_envoi']

