from django.db import models
from django.db.models import Avg, Count, Q, Sum

from conges.models import Conge
from employees.models import Employe
from justification.models import Justification
from presences.models import Presence


class Rapport(models.Model):

    class TypeRapport(models.TextChoices):
        EFFECTIFS      = 'EFFECTIFS',      'Rapport effectifs'
        PRESENCES      = 'PRESENCES',      'Rapport présences'
        ABSENCES       = 'ABSENCES',       'Rapport absences'
        CONGES         = 'CONGES',         'Rapport congés'
        JUSTIFICATIONS = 'JUSTIFICATIONS', 'Rapport justifications'
        SALAIRES       = 'SALAIRES',       'Rapport salaires'
        MENSUEL        = 'MENSUEL',        'Rapport mensuel complet'

    titre         = models.CharField(max_length=200, verbose_name="Titre")
    type_rapport  = models.CharField(
        max_length=30, choices=TypeRapport.choices, verbose_name="Type de rapport"
    )
    description   = models.TextField(blank=True, verbose_name="Description")
    genere_par    = models.ForeignKey(
        Employe, on_delete=models.SET_NULL, null=True,
        related_name='rapports_generes', verbose_name="Généré par"
    )
    date_debut    = models.DateField(null=True, blank=True, verbose_name="Période début")
    date_fin      = models.DateField(null=True, blank=True, verbose_name="Période fin")
    date_creation = models.DateTimeField(auto_now_add=True)
    donnees       = models.JSONField(default=dict, blank=True, verbose_name="Données du rapport")

    def _filtre_periode(self, qs, champ_debut, champ_fin):
        if self.date_debut:
            qs = qs.filter(**{f"{champ_debut}__gte": self.date_debut})
        if self.date_fin:
            qs = qs.filter(**{f"{champ_fin}__lte": self.date_fin})
        return qs

   
    def _donnees_effectifs(self):
        employes_actifs = Employe.objects.filter(is_active=True)
        return {
            'total_actifs':     employes_actifs.count(),
            'total_inactifs':   Employe.objects.filter(is_active=False).count(),
            'total_global':     Employe.objects.count(),
            'par_role':         list(
                Employe.objects.values('role').annotate(total=Count('id')).order_by('-total')
            ),
            'nouveaux_ce_mois': Employe.objects.filter(
                date_joined__month=self.date_debut.month,
                date_joined__year=self.date_debut.year,
            ).count() if self.date_debut else 0,
        }

    def _donnees_presences(self):
        qs = self._filtre_periode(Presence.objects.all(), 'date', 'date')
        total = qs.count()
        presents = qs.filter(statut='PRESENT').count()
        absents  = qs.filter(statut='ABSENT').count()
        retards  = qs.filter(statut='RETARD').count()
        
        return {
            'total':            total,
            'presents':         presents,
            'absents':          absents,
            'retards':          retards,
            'taux_presence':    round((presents / total * 100), 2) if total else 0,
            'taux_absenteisme': round((absents  / total * 100), 2) if total else 0,
            'taux_retard':      round((retards  / total * 100), 2) if total else 0,
            'par_employe':      list(
                qs.values('employe__nom', 'employe__prenom')
                  .annotate(
                      total=Count('id'),
                      nb_presents=Count('id', filter=Q(statut='PRESENT')),
                      nb_absents=Count('id',  filter=Q(statut='ABSENT')),
                      nb_retards=Count('id',  filter=Q(statut='RETARD')),
                  )
                  .order_by('-nb_absents')
            ),
        }

    def _donnees_absences(self):
        qs_absences = self._filtre_periode(Presence.objects.filter(statut='ABSENT'), 'date', 'date')
        qs_toutes = self._filtre_periode(Presence.objects.all(), 'date', 'date')
        
        total_presences = qs_toutes.count()
        total_absences  = qs_absences.count()
        
        qs_justif_validees = self._filtre_periode(
            Justification.objects.filter(statut='VALIDEE'), 
            'date_soumission', 
            'date_soumission'
        )
        absences_justifiees = qs_justif_validees.count()

        return {
            'total_absences':          total_absences,
            'taux_absenteisme':        round((total_absences / total_presences * 100), 2) if total_presences else 0,
            'par_employe':             list(
                qs_absences.values('employe__nom', 'employe__prenom')
                .annotate(nb_absences=Count('id'))
                .order_by('-nb_absences')
            ),
            'absences_justifiees':     absences_justifiees,
            'absences_non_justifiees': max(0, total_absences - absences_justifiees),
        }

    def _donnees_conges(self):
        qs = self._filtre_periode(Conge.objects.all(), 'date_debut', 'date_fin')
        total = qs.count()
        
        return {
            'total':          total,
            'approuves':      qs.filter(statut='APPROUVE').count(),
            'refuses':        qs.filter(statut='REFUSE').count(),
            'en_attente':     qs.filter(statut='EN_ATTENTE').count(),
            'annules':        qs.filter(statut='ANNULE').count(),
            'par_type':       list(
                qs.values('type_conge').annotate(total=Count('id')).order_by('-total')
            ),
            'par_employe':    list(
                qs.values('employe__nom', 'employe__prenom')
                  .annotate(nb_conges=Count('id'))
                  .order_by('-nb_conges')[:10]
            ),
            'taux_approbation': round(
                qs.filter(statut='APPROUVE').count() / total * 100, 2
            ) if total else 0,
        }

    def _donnees_justifications(self):
        qs = self._filtre_periode(Justification.objects.all(), 'date_soumission', 'date_soumission')
        
        return {
            'total':      qs.count(),
            'validees':   qs.filter(statut='VALIDEE').count(),
            'rejetees':   qs.filter(statut='REJETEE').count(),
            'en_attente': qs.filter(statut='EN_ATTENTE').count(),
        }

    def _donnees_salaires(self):
        employes = Employe.objects.filter(is_active=True)

        salaire_field = next(
            (f.name for f in Employe._meta.get_fields()
             if f.name in ('salaire', 'salaire_base', 'remuneration')),
            None
        )

        if not salaire_field:
            return {'erreur': "Aucun champ salaire trouvé sur le modèle Employe."}

        agregats = employes.aggregate(
            masse_salariale=Sum(salaire_field),
            salaire_moyen=Avg(salaire_field),
            salaire_max=models.Max(salaire_field),
            salaire_min=models.Min(salaire_field),
        )

        return {
            'total_employes_payes': employes.count(),
            'masse_salariale':      float(agregats['masse_salariale'] or 0),
            'salaire_moyen':        round(float(agregats['salaire_moyen'] or 0), 2),
            'salaire_max':          float(agregats['salaire_max'] or 0),
            'salaire_min':          float(agregats['salaire_min'] or 0),
            'par_role':             list(
                employes.values('role')
                        .annotate(
                            nb_employes=Count('id'),
                            masse=Sum(salaire_field),
                            moyenne=Avg(salaire_field),
                        )
                        .order_by('-masse')
            ),
        }

    def _donnees_mensuel(self):
        return {
            'effectifs':      self._donnees_effectifs(),
            'presences':      self._donnees_presences(),
            'absences':       self._donnees_absences(),
            'conges':         self._donnees_conges(),
            'justifications': self._donnees_justifications(),
            'salaires':       self._donnees_salaires(),
        }

    
    _GENERATEURS = {
        TypeRapport.EFFECTIFS:      '_donnees_effectifs',
        TypeRapport.PRESENCES:      '_donnees_presences',
        TypeRapport.ABSENCES:       '_donnees_absences',
        TypeRapport.CONGES:         '_donnees_conges',
        TypeRapport.JUSTIFICATIONS: '_donnees_justifications',
        TypeRapport.SALAIRES:       '_donnees_salaires',
        TypeRapport.MENSUEL:        '_donnees_mensuel',
    }

    def genererDonnees(self):
        methode = self._GENERATEURS.get(self.type_rapport)
        if methode:
            self.donnees = getattr(self, methode)()
        else:
            self.donnees = {}
        self.save(update_fields=['donnees'])
        return self.donnees

    def __str__(self):
        return f"{self.titre} — {self.date_creation.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name        = "Rapport"
        verbose_name_plural = "Rapports"
        ordering            = ['-date_creation']