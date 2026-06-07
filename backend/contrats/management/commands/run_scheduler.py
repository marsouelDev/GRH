import schedule
import time
import threading
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Lance le planificateur de tâches en arrière-plan (compatible Windows)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Exécuter une seule fois (pour tester)'
        )

    def handle(self, *args, **options):
        if options['once']:
            self.stdout.write(" Exécution unique de test...")
            self.verification_contrats(7)
            return

        self.stdout.write(self.style.SUCCESS(" Planificateur de tâches démarré..."))
        self.stdout.write("Appuyez sur Ctrl+C pour arrêter.\n")

        # Tâche 1 : Tous les jours à 08h00 (alerte 7 jours)
        schedule.every().day.at("08:00").do(
            self.verification_contrats, jours=7
        )

        # Tâche 2 : Tous les lundis à 09h00 (alerte 30 jours)
        schedule.every().monday.at("09:00").do(
            self.verification_contrats, jours=30
        )

        # Tâche 3 : Toutes les heures (vérification rapide)
        schedule.every().hour.do(
            self.verification_contrats, jours=1
        )

        # Boucle principale
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les 60 secondes

    def verification_contrats(self, jours=7):
        self.stdout.write(
            self.style.WARNING(
                f" [{time.strftime('%H:%M:%S')}] Vérification automatique "
                f"des contrats ({jours} jours)..."
            )
        )
        try:
            call_command('verifier_expiration_contrats', f'--jours={jours}')
            self.stdout.write(self.style.SUCCESS(" Vérification terminée."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f" Erreur : {e}"))