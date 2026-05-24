import string
import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import RH
from .serializers import RHSerializer
from .permissions import IsAdminUserRole

def generer_mot_de_passe(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class RHListCreateAPIView(APIView):
    # Utilisation directe de la classe de permission pour sécuriser l'ensemble des méthodes
    permission_classes = [IsAdminUserRole]

    @extend_schema(summary="Liste des RH", responses=RHSerializer(many=True))
    def get(self, request):
        rh = RH.objects.all().order_by('id')
        serializer = RHSerializer(rh, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Creation d'un RH", request=RHSerializer, responses=RHSerializer)
    def post(self, request):
        serializer = RHSerializer(data=request.data)
        if serializer.is_valid():
            mot_de_passe = generer_mot_de_passe()
            rh = serializer.save(password=mot_de_passe)
            sujet = "Votre compte dans notre plateforme"
            
                      
            login_url = "http://localhost:4200/login"
            
            # Extraction du rôle au format texte propre
            role_texte = rh.get_role_display() if hasattr(rh, 'get_role_display') else str(rh.role)
            
 
            if rh.role == 'RH':
                badge_style = "background-color: #dbeafe; color: #1e40af;"  # Bleu
           

            sujet = "Création de votre compte - RH_Manager"

            
            message_simple = f"""Bonjour {rh.nom},

Votre compte a été créé avec succès sur la plateforme RH_Manager.

Voici vos identifiants de connexion provisoires :
Email : {rh.email}
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
                            <p style="font-size: 16px; margin-top: 0;">Bonjour <b>{rh.nom}</b>,</p>
                            <p style="font-size: 15px; color: #555555;">Votre compte utilisateur a été configuré avec succès. Voici vos paramètres de connexion provisoires :</p>
                            
                            <!-- Encadré des identifiants -->
                            <div style="background-color: #f8fafc; border-left: 4px solid #4f46e5; padding: 15px; margin: 20px 0; border-radius: 0 6px 6px 0;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b; width: 130px;"><b>Identifiant (Email) :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b; font-weight: 500;">{rh.email}</td>
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
            
            email_envoye = True
            try:
                send_mail(
                    sujet,
                    message_simple,             
                    settings.DEFAULT_FROM_EMAIL,
                    [rh.email],
                    fail_silently=False,
                    html_message=html_message  
                )
            except Exception:
                email_envoye = False

            response_data = serializer.data
            if email_envoye:
                response_data["notification"] = f"Compte créé et e-mail de bienvenue ({role_texte}) expédié."
            else:
                response_data["notification"] = f"Compte créé, mais l'envoi de la notification ({role_texte}) a échoué."
                
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RHDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAdminUserRole]

    def get_object(self, id):
        try:
            return RH.objects.get(id=id)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un RH", responses=RHSerializer)
    def get(self, request, id):
        rh = self.get_object(id)
        if not rh:
            return Response(
                {"detail": "rh introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = RHSerializer(rh)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un rh", request=RHSerializer, responses=RHSerializer)
    def put(self, request, id):
        rh = self.get_object(id)
        if not rh:
            return Response(
                {"detail": "RH introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = RHSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="désactivation RH", responses=None)
    def delete(self, request, id):
        rh = self.get_object(id)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = False
        rh.save()
        
        return Response({"detail": "RH désactivé avec succès."}, status=status.HTTP_200_OK)
 
class RHActiverView(APIView):
       
    permission_classes = [IsAdminUserRole]

    @extend_schema(summary="Réactiver un poste archivé (RH/Admin)", responses=RHSerializer)
    def put(self, request, pk):
        try:
            rh = RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return Response({"detail": "Poste introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.est_actif = True
        rh.save()
        return Response({"detail": "Poste réactivé avec succès.","RH": RHSerializer(rh).data}, status=status.HTTP_200_OK)
        