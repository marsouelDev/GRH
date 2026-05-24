from django.db import models
from presences.models import Presence
from django.db.models import Count, Avg
from employees.models import Employe
from justification.models import Justification
from conges.models import Conge

class Rapport(models.Model):
    
    class TypeRapport(models.TextChoices):
        EFFECTIFS  = 'EFFECTIFS', 'Rapport effectifs'
        PRESENCES = 'PRESENCES', 'Rapport présences'
        ABSENCES  = 'ABSENCES','Rapport absences'
        CONGES  = 'CONGES',  'Rapport congés'
        JUSTIFICATIONS= 'JUSTIFICATIONS','Rapport justifications'
        SALAIRES  = 'SALAIRES', 'Rapport salaires'
        MENSUEL = 'MENSUEL', 'Rapport mensuel complet'

    titre   = models.CharField(max_length=200, verbose_name="Titre")
    type_rapport = models.CharField(max_length=30,choices=TypeRapport.choices,verbose_name="Type de rapport")
    description = models.TextField(blank=True, verbose_name="Description")
    genere_par = models.ForeignKey(Employe,on_delete=models.SET_NULL,null=True,related_name='rapports_generes',verbose_name="Généré par")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Période début")
    date_fin  = models.DateField(null=True, blank=True, verbose_name="Période fin")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    donnees  = models.JSONField(default=dict, blank=True, verbose_name="Données du rapport")

    def genererDonnees(self):
        
        data = {}

        if self.type_rapport == self.TypeRapport.EFFECTIFS:
            data = {
                'total_employes': Employe.objects.filter(is_active=True).count(),
                'total_employes_desactive':Employe.objects.filter(is_active=False).count(),
                'par_role': list(Employe.objects.values('role').annotate(total=Count('id'))),
            }

        elif self.type_rapport == self.TypeRapport.PRESENCES:
            ps = Presence.objects.all()
            if self.date_debut: ps = ps.filter(date__gte=self.date_debut)
            if self.date_fin:   ps = ps.filter(date__lte=self.date_fin)
            data = {
                'total':    ps.count(),
                'presents': ps.filter(statut='PRESENT').count(),
                'absents':  ps.filter(statut='ABSENT').count(),
                'retards':  ps.filter(statut='RETARD').count(),
            }

        elif self.type_rapport == self.TypeRapport.CONGES:
            qs = Conge.objects.all()
            if self.date_debut: qs = qs.filter(date_debut__gte=self.date_debut)
            if self.date_fin:   qs = qs.filter(date_fin__lte=self.date_fin)
            data = {
                'total': qs.count(),
                'approuves':  qs.filter(statut='APPROUVE').count(),
                'refuses':  qs.filter(statut='REFUSE').count(),
                'en_attente': qs.filter(statut='EN_ATTENTE').count(),
            }

        elif self.type_rapport == self.TypeRapport.JUSTIFICATIONS:
            qs = Justification.objects.all()
            data = {
                'total':  qs.count(),
                'validees':  qs.filter(statut='VALIDEE').count(),
                'rejetees':  qs.filter(statut='REJETEE').count(),
                'en_attente': qs.filter(statut='EN_ATTENTE').count(),
            }

        self.donnees = data
        self.save()
        return data

    def __str__(self):
        return f"{self.titre} — {self.date_creation.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Rapport"
        ordering     = ['-date_creation']