from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from employees.models import Employe


class Conge(models.Model):

    class TypeConge(models.TextChoices):
        ANNUEL = 'ANNUEL', 'Congé annuel'
        MALADIE = 'MALADIE', 'Congé maladie'
        MATERNITE = 'MATERNITE', 'Congé maternité'
        SANS_SOLDE = 'SANS_SOLDE', 'Sans solde'
        AUTRE = 'AUTRE', 'Autre'

    class StatutConge(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        APPROUVE = 'APPROUVE', 'Approuvé'
        REFUSE = 'REFUSE', 'Refusé'
        ANNULE = 'ANNULE', 'Annulé'

    employe = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        related_name='conges',
        verbose_name="Employé"
    )
    type_conge = models.CharField(
        max_length=20,
        choices=TypeConge.choices,
        verbose_name="Type de congé"
    )
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    motif = models.TextField(blank=True, verbose_name="Motif")
    
    statut = models.CharField(
        max_length=20,
        choices=StatutConge.choices,
        default=StatutConge.EN_ATTENTE,
        verbose_name="Statut"
    )
    date_demande = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de demande"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire (motif de refus ou approbation)"
    )
    
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Type de validateur"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID du validateur"
    )
    valide_par = GenericForeignKey('content_type', 'object_id')
    date_validation = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de validation"
    )

    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        ordering = ['-date_demande']
        indexes = [
            models.Index(fields=['employe', 'statut']),
            models.Index(fields=['date_debut', 'date_fin']),
        ]

    def __str__(self):
        return f"{self.employe} — {self.get_type_conge_display()} — {self.date_debut} au {self.date_fin} ({self.get_statut_display()})"

    def calculerDuree(self):
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days + 1
        return 0

    def peut_etre_modifie(self):
        return self.statut == self.StatutConge.EN_ATTENTE

    def peut_etre_annule(self):
        return self.statut in [
            self.StatutConge.EN_ATTENTE,
            self.StatutConge.APPROUVE
        ]

    def approuver(self, rh=None, commentaire=''):
        
        if self.statut != self.StatutConge.EN_ATTENTE:
            raise ValueError("Ce congé a déjà été traité")
        
        self.statut = self.StatutConge.APPROUVE
        self.commentaire = commentaire
        self.date_validation = timezone.now()
        
        if rh:
            self.content_type = ContentType.objects.get_for_model(rh)
            self.object_id = rh.pk
        
        self.save()

    def refuser(self, rh=None, commentaire=''):
      
        if self.statut != self.StatutConge.EN_ATTENTE:
            raise ValueError("Ce congé a déjà été traité")
        
        self.statut = self.StatutConge.REFUSE
        self.commentaire = commentaire
        self.date_validation = timezone.now()
        
        if rh:
            self.content_type = ContentType.objects.get_for_model(rh)
            self.object_id = rh.pk
        
        self.save()

    def annuler(self):
        if self.statut == self.StatutConge.ANNULE:
            raise ValueError("Ce congé est déjà annulé")
        
        self.statut = self.StatutConge.ANNULE
        self.date_validation = timezone.now()
        self.save()

    def get_valide_par_nom(self):
        if self.valide_par:
            nom = getattr(self.valide_par, 'nom', '')
            prenom = getattr(self.valide_par, 'prenom', '')
            if nom or prenom:
                return f"{nom} {prenom}".strip()
            # Fallback pour User Django standard
            first_name = getattr(self.valide_par, 'first_name', '')
            last_name = getattr(self.valide_par, 'last_name', '')
            if first_name or last_name:
                return f"{first_name} {last_name}".strip()
            email = getattr(self.valide_par, 'email', '')
            if email:
                return email
        return None

    def est_en_retard(self):
        """Vérifie si le congé est en retard (date de début passée)"""
        if self.statut == self.StatutConge.EN_ATTENTE:
            return self.date_debut < timezone.now().date()
        return False