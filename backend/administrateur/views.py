import random
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .models import Administrateur
from .serializers import AdministrateurSerializer, ChangeAdminSerializer
from .permissions import IsAdminUserRole


def generer_mot_de_passe(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class AdministrateurListCreateAPIView(APIView):
    permission_classes = [IsAdminUserRole]
    pagination_class = PageNumberPagination
    serializer_class = AdministrateurSerializer

    @extend_schema(summary="Liste des Admin", responses=AdministrateurSerializer(many=True))
    def get(self, request):
        administrateurs = Administrateur.objects.all().order_by('id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(administrateurs, request, view=self)

        if page is not None:
            serializer = AdministrateurSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AdministrateurSerializer(administrateurs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Créer un administrateur", request=AdministrateurSerializer, responses=AdministrateurSerializer)
    def post(self, request):
        serializer = AdministrateurSerializer(data=request.data)
        if serializer.is_valid():
            mot_de_passe = generer_mot_de_passe()
            admin = serializer.save(password=mot_de_passe)

            login_url = "https://gestion-culqxqs4x-marsouel-s-projects.vercel.app/login"
            role_texte = admin.get_role_display() if hasattr(admin, 'get_role_display') else str(admin.role)

            if admin.role == 'ADMIN':
                badge_style = "background-color: #ef4444; color: #ffffff;"
            else:
                badge_style = "background-color: #3b82f6; color: #ffffff;"

            sujet = "Création de votre compte - RH_Manager"

            message_simple = f"""Bonjour {admin.nom},

Votre compte a été créé avec succès sur la plateforme RH_Manager.

Voici vos identifiants de connexion provisoires :
Email : {admin.email}
Mot de passe temporaire : {mot_de_passe}
Rôle : {role_texte}

Veuillez vous connecter pour modifier votre mot de passe : {login_url}"""

            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e1e4e8;">
                        <div style="background-color: #4f46e5; padding: 25px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700;">RH_Manager</h1>
                            <p style="color: #c7d2fe; margin: 5px 0 0 0; font-size: 14px;">Système de Gestion des Ressources Humaines</p>
                        </div>
                        <div style="padding: 30px; color: #333333; line-height: 1.6;">
                            <p style="font-size: 16px; margin-top: 0;">Bonjour <b>{admin.nom}</b>,</p>
                            <p style="font-size: 15px; color: #555555;">Votre compte utilisateur a été configuré avec succès. Voici vos paramètres de connexion provisoires :</p>
                            <div style="background-color: #f8fafc; border-left: 4px solid #4f46e5; padding: 15px; margin: 20px 0; border-radius: 0 6px 6px 0;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                    <tr>
                                        <td style="padding: 5px 0; color: #64748b; width: 130px;"><b>Identifiant (Email) :</b></td>
                                        <td style="padding: 5px 0; color: #1e293b; font-weight: 500;">{admin.email}</td>
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
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{login_url}" style="background-color: #4f46e5; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 15px; display: inline-block;">
                                    Me connecter à mon espace numérique
                                </a>
                            </div>
                            <p style="font-size: 13px; color: #b91c1c; background-color: #fef2f2; padding: 12px; border-radius: 6px; margin-bottom: 0;">
                                ⚠️ <b>Sécurité :</b> Ce mot de passe est confidentiel et temporaire. Il vous sera demandé de le remplacer dès votre première connexion.
                            </p>
                        </div>
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
                    [admin.email],
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


class AdministrateurDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAdminUserRole]

    def get_object(self, id):
        try:
            return Administrateur.objects.get(id=id)
        except Administrateur.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un admin", responses=AdministrateurSerializer)
    def get(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdministrateurSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un admin", request=AdministrateurSerializer, responses=AdministrateurSerializer)
    def put(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdministrateurSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        admin.delete()
        return Response({"detail": "Administrateur supprimé."}, status=status.HTTP_204_NO_CONTENT)

class AdminChangeProfilAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Administrateur.objects.get(id=id)
        except Administrateur.DoesNotExist:
            return None

    @extend_schema(summary="Modifier son propre profil", request=ChangeAdminSerializer, responses=ChangeAdminSerializer)
    def put(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Seul l'admin lui-même ou un super-admin peut modifier
        if request.user.id != admin.id and request.user.role not in ['ADMIN']:
            return Response({"detail": "Accès interdit."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChangeAdminSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)