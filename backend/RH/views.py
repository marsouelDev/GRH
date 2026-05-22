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
            message = f"""Bonjour {rh.nom},

Votre compte a été créé sur la plateforme de Systeme de Gestion des Ressource Humaine nommée RH_Manager. Voici vos informations de connexion :

Email : {rh.email}
Mot de passe temporaire : {mot_de_passe}
Rôle : {rh.get_role_display() if hasattr(rh, 'get_role_display') else 'RH'}

Changez votre mot de passe dès votre première connexion pour plus de sécurité."""
            
            email_envoye = True
            try:
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [rh.email],
                    fail_silently=False
                )
            except Exception:
                email_envoye = False

            response_data = serializer.data
            if email_envoye:
                response_data["notification"] = "RH créé et e-mail envoyé."
            else:
                response_data["notification"] = "RH créé, mais l'e-mail n'a pas pu être envoyé."
                
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
