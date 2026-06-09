import string
import secrets
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import Employe
from .serializers import ChangeEmployeSerializer, EmployeSerializer
from .permissions import IsRhOrAdmin
from contrats.models import Contrat
from conges.models import Conge
from GRH.utils import envoyer_email_brevo

logger = logging.getLogger(__name__)


def generer_mot_de_passe(length=12):
    """Génère un mot de passe sécurisé avec lettres, chiffres et caractères spéciaux."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))


class EmployeListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOrAdmin()]

    @extend_schema(summary="Liste des employés", responses=EmployeSerializer(many=True))
    def get(self, request):
        employes = Employe.objects.all().order_by('id')
        serializer = EmployeSerializer(employes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Créer un employé", request=EmployeSerializer, responses=EmployeSerializer)
    def post(self, request):
        serializer = EmployeSerializer(data=request.data)
        if serializer.is_valid():
            mot_de_passe = generer_mot_de_passe()

            # 1. Création de l'employé
            employe = serializer.save()
            
            # 2. Hachage sécurisé du mot de passe (CRITIQUE)
            employe.set_password(mot_de_passe)
            employe.save(update_fields=['password'])

            login_url = "https://gestion-rh-lac.vercel.app/login"
            
            # Extraction du rôle au format texte propre
            role_texte = employe.get_role_display() if hasattr(employe, 'get_role_display') else str(employe.role)
            
            # Style du badge selon le rôle
            if employe.role == 'EMPLOYE':
                badge_style = "background-color: #28a745; color: #ffffff;"
            else:
                badge_style = "background-color: #6c757d; color: #ffffff;"

            sujet = "Création de votre compte - RH_Manager"
            
            message_simple = f"""Bonjour {employe.nom},

Votre compte a été créé avec succès sur la plateforme RH_Manager.

Voici vos identifiants de connexion provisoires :
Email : {employe.email}
Mot de passe temporaire : {mot_de_passe}
Rôle : {role_texte}

Veuillez vous connecter pour modifier votre mot de passe : {login_url}"""

            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e1e4e8;">
                        
                        <!-- En-tête -->
                        <div style="background-color: #4f46e5; padding: 25px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700;">RH_Manager</h1>
                            <p style="color: #c7d2fe; margin: 5px 0 0 0; font-size: 14px;">Système de Gestion des Ressources Humaines</p>
                        </div>
                        
                        <!-- Corps du message -->
                        <div style="padding: 30px; color: #333333; line-height: 1.6;">
                            <p style="font-size: 16px; margin-top: 0;">Bonjour <b>{employe.nom}</b>,</p>
                            <p style="font-size: 15px; color: #555555;">Votre compte utilisateur a été configuré avec succès. Voici vos paramètres de connexion provisoires :</p>
                            
                            <!-- Encadré des identifiants -->
                            <div style="background-color: #f8fafc; border-left: 4px solid #4f46e5; padding: 15px; margin: 20px 0; border-radius: 0 6px 6px 0;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b; width: 130px;"><b>Identifiant (Email) :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b; font-weight: 500;">{employe.email}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b;"><b>Mot de passe :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b;"><code style="background-color: #e2e8f0; padding: 3px 6px; border-radius: 4px; font-family: monospace; font-size: 14px; font-weight: bold;">{mot_de_passe}</code></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b;"><b>Espace de travail :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b;"><span style="{badge_style} padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; display: inline-block;">{role_texte}</span></td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Bouton d'action -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{login_url}" style="background-color: #4f46e5; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 15px; display: inline-block;">
                                    Me connecter à mon espace numérique
                                </a>
                            </div>
                            
                            <!-- Notice de sécurité -->
                            <p style="font-size: 13px; color: #b91c1c; background-color: #fef2f2; padding: 12px; border-radius: 6px; margin-bottom: 0;">
                                ⚠️ <b>Sécurité :</b> Ce mot de passe est confidentiel et temporaire. Il vous sera demandé de le remplacer dès votre première connexion.
                            </p>
                        </div>
                        
                        <!-- Pied de page -->
                        <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; font-size: 11px; color: #94a3b8;">Message de sécurité automatique envoyé par RH_Manager — Merci de ne pas y répondre.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Envoi via l'API HTTP Brevo (contourne le blocage SMTP de Render)
            email_envoye = envoyer_email_brevo(
                destinataire_email=employe.email,
                destinataire_nom=employe.nom,
                sujet=sujet,
                message_html=html_message,
                message_texte=message_simple
            )

            response_data = serializer.data
            if email_envoye:
                response_data["notification"] = f"Compte créé et e-mail de bienvenue ({role_texte}) expédié."
            else:
                response_data["notification"] = f"Compte créé, mais l'envoi de la notification ({role_texte}) a échoué."
                
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeDetailUpdateDeleteActiveAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOrAdmin()]

    def get_object(self, id):
        try:
            return Employe.objects.get(id=id)
        except Employe.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un employé", responses=EmployeSerializer)
    def get(self, request, id):
        employe = self.get_object(id)
        if not employe:
            return Response({"detail": "Employé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeSerializer(employe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un employé", request=EmployeSerializer, responses=EmployeSerializer)
    def put(self, request, id):
        employe = self.get_object(id)
        if not employe:
            return Response({"detail": "Employé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeSerializer(employe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Désactiver un employé (soft delete)", responses=None)
    def delete(self, request, id):
        employe = self.get_object(id)
        if not employe:
            return Response({"detail": "Employé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        employe.is_active = False
        employe.save()
        return Response({"detail": "Employé désactivé avec succès."}, status=status.HTTP_200_OK)


class EmployeActiverView(APIView):
    permission_classes = [IsRhOrAdmin]

    @extend_schema(summary="Réactiver un employé archivé (RH/Admin)", responses=EmployeSerializer)
    def put(self, request, id):
        try:
            emp = Employe.objects.get(id=id)
        except Employe.DoesNotExist:
            return Response({"detail": "Employé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        emp.is_active = True
        emp.save()
        return Response({
            "detail": "Employé réactivé avec succès.",
            "Employe": EmployeSerializer(emp).data
        }, status=status.HTTP_200_OK)


class EmployeChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Employe.objects.get(id=id)
        except Employe.DoesNotExist:
            return None
    
    @extend_schema(summary="Modifier son propre profil", request=ChangeEmployeSerializer, responses=ChangeEmployeSerializer)
    def put(self, request, id):
        employe = self.get_object(id)
        if not employe:
            return Response({"detail": "Employé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id != employe.id and request.user.role not in ['ADMIN', 'RH']:
            return Response({"detail": "Accès interdit."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChangeEmployeSerializer(employe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        data = {}

        # 1. Statistiques globales pour les RH et ADMIN
        if role in ['RH', 'ADMIN'] or user.is_superuser:
            data['employes_totaux'] = Employe.objects.count()
            data['contrats_actifs'] = Contrat.objects.filter(statut='ACTIF').count()
            data['conges_en_attente'] = Conge.objects.filter(statut='EN_ATTENTE').count()
        
        # 2. Statistiques privées pour un simple EMPLOYE
        else:
            # TODO: Remplacer 18 par le vrai calcul basé sur votre modèle de solde de congés
            data['mes_conges_restants'] = 18  
            data['mes_demandes_en_attente'] = Conge.objects.filter(employe=user, statut='EN_ATTENTE').count()

        return Response(data)