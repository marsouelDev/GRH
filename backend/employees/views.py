import string
import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Employe
from .serializers import EmployeSerializer
from .permissions import IsRhOrAdmin


def generer_mot_de_passe(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


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

            serializer.validated_data['password'] = mot_de_passe
            employe = serializer.save()

            sujet = "Votre compte RH_Manager"
            message = (
                f"Bonjour {employe.nom},\n\n"
                f"Votre compte a été créé sur la plateforme RH_Manager.\n\n"
                f"Email : {employe.email}\n"
                f"Mot de passe temporaire : {mot_de_passe}\n"
                f"Rôle : {employe.get_role_display() if hasattr(employe, 'get_role_display') else 'Employé'}\n\n"
                f"Changez votre mot de passe dès votre première connexion."
            )

            email_envoye = True
            try:
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [employe.email],
                    fail_silently=False,
                )
            except Exception:
                email_envoye = False

           
            response_data = dict(serializer.data)
            response_data["notification"] = (
                "Employé créé et e-mail envoyé."
                if email_envoye
                else "Employé créé, mais l'e-mail n'a pas pu être envoyé."
            )

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeDetailUpdateDeleteAPIView(APIView):

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
        # partial=True → seuls les champs envoyés sont mis à jour
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