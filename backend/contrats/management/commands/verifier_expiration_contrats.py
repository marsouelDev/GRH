from datetime import date, timedelta
from django.core.management.base import BaseCommand
from contrats.models import Contrat
from contrats.services import notifier_rh_sur_contrat_expiration
from RH.models import RH
from GRH.utils import envoyer_email_brevo


class Command(BaseCommand):
    help = 'Vérifie les contrats arrivant à expiration et notifie tous les RH'

    def add_arguments(self, parser):
        parser.add_argument(
            '--jours',
            type=int,
            default=7,
            help='Nombre de jours avant expiration pour alerter (défaut: 7)'
        )

    def handle(self, *args, **options):
        jours_alerte = options['jours']
        aujourdhui = date.today()
        date_limite = aujourdhui + timedelta(days=jours_alerte)
        
        self.stdout.write(f"🔍 Vérification des contrats expirant avant le {date_limite}...")
        
        # 1) Contrats ACTIFS qui expirent dans les N prochains jours
        contrats_expirants = Contrat.objects.filter(
            statut='ACTIF',
            date_fin__isnull=False,
            date_fin__lte=date_limite,
            date_fin__gte=aujourdhui
        ).select_related('employe', 'poste')
        
        # 2) Contrats déjà expirés mais encore marqués ACTIF
        contrats_expires = Contrat.objects.filter(
            statut='ACTIF',
            date_fin__isnull=False,
            date_fin__lt=aujourdhui
        ).select_related('employe', 'poste')
        
        nb_expirants = contrats_expirants.count()
        nb_expires = contrats_expires.count()
        total = nb_expirants + nb_expires
        
        compteur = 0
        
        # Notifier pour les contrats expirant bientôt
        for contrat in contrats_expirants:
            self.stdout.write(f"     Alerte pour {contrat.employe.nom} (expire le {contrat.date_fin})")
            notifier_rh_sur_contrat_expiration(contrat)
            compteur += 1
        
        # Notifier pour les contrats déjà expirés
        for contrat in contrats_expires:
            self.stdout.write(f"Contrat EXPIRÉ : {contrat.employe.nom} (expiré le {contrat.date_fin})")
            notifier_rh_sur_contrat_expiration(contrat)
            compteur += 1
        
        # Envoyer un email récapitulatif à tous les RH
        if total > 0:
            nb_envoyes = self._envoyer_recap_email(total, nb_expirants, nb_expires)
            self.stdout.write(self.style.SUCCESS(f"\n✨ {compteur} notification(s) individuelle(s) envoyée(s)"))
            self.stdout.write(self.style.SUCCESS(f"📧 Email récapitulatif envoyé à {nb_envoyes} RH"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Aucun contrat nécessitant une attention"))
    
    def _envoyer_recap_email(self, total, nb_expirants, nb_expires):
        """Envoie un email récapitulatif HTML stylisé à tous les RH via l'API HTTP Brevo"""
        rhs = RH.objects.filter(is_active=True)
        
        # URL correcte du frontend Vercel
        frontend_url = "https://gestion-rh-lac.vercel.app"
        sujet = f"[RH_Manager] {total} contrat(s) nécessitent votre attention"
        
        # Version texte brut (fallback)
        message = (
            f"Bonjour,\n\n"
            f"Un contrôle automatique a détecté :\n"
            f"  • {nb_expirants} contrat(s) expirant bientôt\n"
            f"  • {nb_expires} contrat(s) déjà expiré(s)\n\n"
            f"Connectez-vous à RH_Manager pour consulter les détails :\n{frontend_url}\n\n"
            f"Cordialement,\nL'équipe RH_Manager"
        )

        # Version HTML (Design amélioré)
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: 'Segoe UI', Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; max-width: 100%;">
                            
                            <!-- En-tête -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 32px 24px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">RH_Manager</h1>
                                    <p style="color: #bfdbfe; margin: 8px 0 0 0; font-size: 14px; font-weight: 500;">Gestion des Ressources Humaines</p>
                                </td>
                            </tr>

                            <!-- Corps du message -->
                            <tr>
                                <td style="padding: 32px 24px; color: #334155;">
                                    <h2 style="color: #0f172a; font-size: 20px; margin-top: 0; margin-bottom: 16px; font-weight: 700;">Bonjour,</h2>
                                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 24px;">
                                        Un contrôle automatique a détecté des contrats nécessitant votre attention immédiate :
                                    </p>

                                    <!-- Blocs de statistiques -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 32px;">
                                        <tr>
                                            <td width="48%" style="padding: 8px; vertical-align: top;">
                                                <div style="background-color: #fffbeb; border-left: 4px solid #d97706; padding: 20px 16px; border-radius: 8px;">
                                                    <strong style="color: #d97706; font-size: 32px; display: block; margin-bottom: 4px; font-weight: 800;">{nb_expirants}</strong>
                                                    <span style="color: #92400e; font-size: 13px; font-weight: 600;">Contrat(s) expirant bientôt</span>
                                                </div>
                                            </td>
                                            <td width="4%"></td>
                                            <td width="48%" style="padding: 8px; vertical-align: top;">
                                                <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 20px 16px; border-radius: 8px;">
                                                    <strong style="color: #dc2626; font-size: 32px; display: block; margin-bottom: 4px; font-weight: 800;">{nb_expires}</strong>
                                                    <span style="color: #991b1b; font-size: 13px; font-weight: 600;">Contrat(s) déjà expiré(s)</span>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>

                                    <!-- Bouton d'action -->
                                    <div style="text-align: center; margin: 32px 0;">
                                        <a href="{frontend_url}/contrats" style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 700; font-size: 15px; display: inline-block; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);">
                                            Consulter le tableau de bord &rarr;
                                        </a>
                                    </div>

                                    <p style="font-size: 14px; color: #64748b; margin-top: 32px; line-height: 1.6;">
                                        Cordialement,<br>
                                        <strong style="color: #0f172a;">L'équipe RH_Manager</strong>
                                    </p>
                                </td>
                            </tr>

                            <!-- Pied de page -->
                            <tr>
                                <td style="background-color: #f8fafc; padding: 20px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
                                    <p style="margin: 0; font-size: 12px; color: #94a3b8;">
                                        Ceci est un email automatique généré par le système RH_Manager. Merci de ne pas y répondre.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        '''
        
        # Envoi à chaque RH individuellement via l'API HTTP Brevo
        nb_envoyes = 0
        for rh in rhs:
            if not rh.email:
                continue
            
            success = envoyer_email_brevo(
                destinataire_email=rh.email,
                destinataire_nom=rh.nom,
                sujet=sujet,
                message_html=html_message,
                message_texte=message
            )
            
            if success:
                nb_envoyes += 1
                self.stdout.write(self.style.SUCCESS(f"  Email envoyé à {rh.email}"))
            else:
                self.stderr.write(self.style.ERROR(f"  Échec envoi à {rh.email}"))
        
        return nb_envoyes