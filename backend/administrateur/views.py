import random
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination 
from .models import Administrateur
from .serializers import AdministrateurSerializer
from .permissions import IsAdminUserRole
from drf_spectacular.utils import extend_schema 
from django.core.mail import send_mail
from django.conf import settings


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
           
            sujet = "Votre compte dans notre plateforme "
            message = f"""Bonjour {admin.nom},

Votre compte a été créé sur la plateforme de Systeme de Gestion des Ressource Humaine nommée RH_Manager. Voici vos informations de connexion :

Email : {admin.email}
Mot de passe temporaire : {mot_de_passe}
Rôle : {admin.get_role_display() if hasattr(admin, 'get_role_display') else 'Employé'}

Changez votre mot de passe dès votre première connexion pour plus de sécurité."""
            
            
            email_envoye = True
            try:
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.email],
                    fail_silently=False
                )
            except Exception:
                email_envoye = False

            
            response_data = serializer.data
            if email_envoye:
                response_data["notification"] = "Administrateur créé et e-mail envoyé."
            else:
                response_data["notification"] = "Administrateur créé, mais l'e-mail n'a pas pu être envoyé."
                
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdministrateurDetailUodateDeleteAPIView(APIView):
    permission_classes = [IsAdminUserRole]

    def get_object(self, id):
        try:
            return Administrateur.objects.get(id=id)
        except Administrateur.DoesNotExist:
            return None
    @extend_schema(summary="Détail d'un admin",responses=AdministrateurSerializer,)
    def get(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdministrateurSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @extend_schema(  summary="Modifier un admin",request=AdministrateurSerializer,responses=AdministrateurSerializer, )
    def put(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
      
        serializer = AdministrateurSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(summary="Supprimer un admin",responses=None,)
    def delete(self, request, id):
       
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        
        admin.is_active = False
        admin.save()
        
        return Response({"detail": "Administrateur désactivé avec succès."}, status=status.HTTP_200_OK)
