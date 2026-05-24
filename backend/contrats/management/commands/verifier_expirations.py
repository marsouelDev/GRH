from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from contrats.models import Contrat

class Command(BaseCommand):
    help = "Vérifie les CDD/Stages expirant dans 15 jours et alerte la RH."

    def handle(self, *args, **options):
        cible = date.today() + timedelta(days=2)
        contrats = Contrat.objects.filter(type_contrat__in=['CDD', 'STAGE'], statut='ACTIF', date_fin=cible).select_related('employe')

        for c in contrats:
            sujet = f"[ALERTE] Échéance contrat : {c.employe.nom} {c.employe.prenom}"
            message = f"Le contrat de {c.employe.nom} ({c.type_contrat}) au poste de {c.poste} prend fin le {c.date_fin}."
            send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            self.stdout.write(f"Email envoyé pour {c.employe.nom}")
