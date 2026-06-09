import string
import secrets
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import RH
from .serializers import ChangeRhSerializer, RHSerializer
from .permissions import IsAdminUserRole
from employees.permissions import IsRhOrAdmin
from GRH.utils import envoyer_email_brevo

logger = logging.getLogger(__name__)


def generer_mot_de_passe(length=12):
    """Génère un mot de passe sécurisé avec lettres, chiffres et caractères spéciaux."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))


class RHListCreateAPIView(APIView):
    permission_classes = [IsRhOrAdmin]

    @extend_schema(summary="Liste des RH", responses=RHSerializer(many=True))
    def get(self, request):
        rhs = RH.objects.all().order_by('id')
        serializer = RHSerializer(rhs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Création d'un RH", request=RHSerializer, responses=RHSerializer)
    def post(self, request):
        serializer = RHSerializer(data=request.data)
        if serializer.is_valid():
            mot_de_passe = generer_mot_de_passe()
            
            # 1. Création de l'instance RH
            rh = serializer.save()
            
            # 2. Hachage sécurisé du mot de passe (CRITIQUE)
            rh.set_password(mot_de_passe)
            rh.save(update_fields=['password'])
            
            login_url = "https://gestion-rh-lac.vercel.app/login"
            role_texte = rh.get_role_display() if hasattr(rh, 'get_role_display') else str(rh.role)
            
            if rh.role == 'RH':
                badge_style = "background-color: #dbeafe; color: #1e40af;"
            else:
                badge_style = "background-color: #fef3c7; color: #92400e;"

            sujet = "Création de votre compte - RH_Manager"
            
            message_simple = f"""Bonjour {rh.nom},

Votre compte a été créé avec succès sur la plateforme RH_Manager.

Identifiants :
Email : {rh.email}
Mot de passe temporaire : {mot_de_passe}
Rôle : {role_texte}

Connectez-vous : {login_url}"""

            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e1e4e8;">
                        <div style="background-color: #4f46e5; padding: 25px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700;">RH_Manager</h1>
                            <p style="color: #c7d2fe; margin: 5px 0 0 0; font-size: 14px;">Système de Gestion des Ressources Humaines</p>
                        </div>
                        <div style="padding: 30px; color: #333333; line-height: 1.6;">
                            <p style="font-size: 16px; margin-top: 0;">Bonjour <b>{rh.nom}</b>,</p>
                            <p style="font-size: 15px; color: #555555;">Votre compte a été créé. Voici vos identifiants :</p>
                            <div style="background-color: #f8fafc; border-left: 4px solid #4f46e5; padding: 15px; margin: 20px 0; border-radius: 0 6px 6px 0;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b; width: 130px;"><b>Email :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b; font-weight: 500;">{rh.email}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b;"><b>Mot de passe :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b;"><code style="background-color: #e2e8f0; padding: 3px 6px; border-radius: 4px; font-family: monospace; font-size: 14px; font-weight: bold;">{mot_de_passe}</code></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b;"><b>Rôle :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b;"><span style="{badge_style} padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; display: inline-block;">{role_texte}</span></td>
                                    </tr>
                                </table>
                            </div>
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{login_url}" style="background-color: #4f46e5; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 15px; display: inline-block;">
                                    Me connecter
                                </a>
                            </div>
                            <p style="font-size: 13px; color: #b91c1c; background-color: #fef2f2; padding: 12px; border-radius: 6px;">
                                ⚠️ <b>Sécurité :</b> Changez votre mot de passe dès la première connexion.
                            </p>
                        </div>
                        <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; font-size: 11px; color: #94a3b8;">RH_Manager — Message automatique</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Envoi via l'API HTTP Brevo (contourne le blocage SMTP de Render)
            email_envoye = envoyer_email_brevo(
                destinataire_email=rh.email,
                destinataire_nom=rh.nom,
                sujet=sujet,
                message_html=html_message,
                message_texte=message_simple
            )

            response_data = serializer.data
            if email_envoye:
                response_data["notification"] = f"Compte créé. Email envoyé avec succès."
            else:
                response_data["notification"] = f"Compte créé avec succès, mais l'envoi de la notification a échoué."

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RHDetailUpdateDeleteAPIView(APIView):
    """Détail et modification — Admin et RH peuvent accéder"""
    permission_classes = [IsRhOrAdmin]

    def get_object(self, pk):
        try:
            return RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un RH", responses=RHSerializer)
    def get(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(RHSerializer(rh).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un RH", request=RHSerializer, responses=RHSerializer)
    def put(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RHSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Désactiver un RH (Admin uniquement)", responses=None)
    def delete(self, request, pk):
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Seul un administrateur peut désactiver un compte."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = False
        rh.save()
        
        return Response({"detail": "RH désactivé avec succès."}, status=status.HTTP_200_OK)


class RHActiverView(APIView):
    """Réactivation — ADMIN UNIQUEMENT"""
    permission_classes = [IsAdminUserRole]

    @extend_schema(summary="Réactiver un RH (Admin uniquement)", responses=RHSerializer)
    def put(self, request, pk):
        try:
            rh = RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = True
        rh.save()
        
        return Response({
            "detail": "RH réactivé avec succès.",
            "RH": RHSerializer(rh).data
        }, status=status.HTTP_200_OK)


class RhChangeAPIView(APIView):
    permission_classes = [IsRhOrAdmin]

    def get_object(self, pk):
        try:
            return RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Modifier son propre profil", request=ChangeRhSerializer, responses=ChangeRhSerializer)
    def put(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id != rh.id:
            return Response(
                {"detail": "Vous ne pouvez modifier que votre propre profil."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChangeRhSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RHDetailUpdateDeleteAPIView(APIView):
    """Détail et modification — Admin et RH peuvent accéder"""
    permission_classes = [IsRhOrAdmin]

    def get_object(self, pk):
        try:
            return RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un RH", responses=RHSerializer)
    def get(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(RHSerializer(rh).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un RH", request=RHSerializer, responses=RHSerializer)
    def put(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RHSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Désactiver un RH (Admin uniquement)", responses=None)
    def delete(self, request, pk):
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Seul un administrateur peut désactiver un compte."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = False
        rh.save()
        
        return Response({"detail": "RH désactivé avec succès."}, status=status.HTTP_200_OK)


class RHActiverView(APIView):
    """Réactivation — ADMIN UNIQUEMENT"""
    permission_classes = [IsAdminUserRole]

    @extend_schema(summary="Réactiver un RH (Admin uniquement)", responses=RHSerializer)
    def put(self, request, pk):
        try:
            rh = RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = True
        rh.save()
        
        return Response({
            "detail": "RH réactivé avec succès.",
            "RH": RHSerializer(rh).data
        }, status=status.HTTP_200_OK)


class RhChangeAPIView(APIView):
    permission_classes = [IsRhOrAdmin]

    def get_object(self, pk):
        try:
            return RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Modifier son propre profil", request=ChangeRhSerializer, responses=ChangeRhSerializer)
    def put(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id != rh.id:
            return Response(
                {"detail": "Vous ne pouvez modifier que votre propre profil."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChangeRhSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RHDetailUpdateDeleteAPIView(APIView):
    """Détail et modification — Admin et RH peuvent accéder"""
    permission_classes = [IsRhOrAdmin]

    def get_object(self, pk):
        try:
            return RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un RH", responses=RHSerializer)
    def get(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(RHSerializer(rh).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un RH", request=RHSerializer, responses=RHSerializer)
    def put(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RHSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Désactiver un RH (Admin uniquement)", responses=None)
    def delete(self, request, pk):
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Seul un administrateur peut désactiver un compte."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = False
        rh.save()
        
        return Response({"detail": "RH désactivé avec succès."}, status=status.HTTP_200_OK)


class RHActiverView(APIView):
    """Réactivation — ADMIN UNIQUEMENT"""
    permission_classes = [IsAdminUserRole]

    @extend_schema(summary="Réactiver un RH (Admin uniquement)", responses=RHSerializer)
    def put(self, request, pk):
        try:
            rh = RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rh.is_active = True
        rh.save()
        
        return Response({
            "detail": "RH réactivé avec succès.",
            "RH": RHSerializer(rh).data
        }, status=status.HTTP_200_OK)


class RhChangeAPIView(APIView):
  
    permission_classes = [IsRhOrAdmin]

    def get_object(self, pk):
        try:
            return RH.objects.get(pk=pk)
        except RH.DoesNotExist:
            return None

    @extend_schema(summary="Modifier son propre profil", request=ChangeRhSerializer, responses=ChangeRhSerializer)
    def put(self, request, pk):
        rh = self.get_object(pk)
        if not rh:
            return Response({"detail": "RH introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id != rh.id:
            return Response(
                {"detail": "Vous ne pouvez modifier que votre propre profil."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChangeRhSerializer(rh, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)