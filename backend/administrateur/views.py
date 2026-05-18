from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination 
from .models import Administrateur
from .serializers import AdministrateurSerializer
from .permissions import IsAdminUserRole 

class AdministrateurListCreateAPIView(APIView):
    permission_classes = [IsAdminUserRole]
    pagination_class = PageNumberPagination 
    serializer_class = AdministrateurSerializer 

    def get(self, request):
        administrateurs = Administrateur.objects.all().order_by('id') 
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(administrateurs, request, view=self)
        
        if page is not None:
            serializer = AdministrateurSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = AdministrateurSerializer(administrateurs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AdministrateurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdministrateurDetailUodateDeleteAPIView(APIView):
    permission_classes = [IsAdminUserRole]

    def get_object(self, id):
        try:
            return Administrateur.objects.get(id=id)
        except Administrateur.DoesNotExist:
            return None

    def get(self, request, id):
        admin = self.get_object(id)
        if not admin:
            return Response({"detail": "Administrateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdministrateurSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        
        
        admin.is_active = False
        admin.save()
        
        return Response({"detail": "Administrateur désactivé avec succès."}, status=status.HTTP_200_OK)
