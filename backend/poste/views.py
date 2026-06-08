from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Poste
from .serializers import PosteSerializer
from contrats.permissions import IsRhOnlyUserRole


class PosteListCreateView(APIView):
   
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOnlyUserRole()]

    @extend_schema(
        summary="Liste des postes", 
        responses=PosteSerializer(many=True),
        parameters=[
            OpenApiParameter(name='actif', description="Mettre 'all' pour inclure les postes archivés", required=False, type=str)
        ]
    )
    def get(self, request):
        qs = Poste.objects.filter(est_actif=True)
        actif = request.query_params.get('actif')
        if actif is not None:
            qs = Poste.objects.all() if actif == 'all' else qs
        return Response(PosteSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Créer un poste (RH/Admin)", request=PosteSerializer, responses=PosteSerializer)
    def post(self, request):
        serializer = PosteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PosteDetailUpdateDeleteView(APIView):
 
   
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOnlyUserRole()]

    def get_object(self, pk):
        try: return Poste.objects.get(pk=pk)
        except Poste.DoesNotExist: return None

    @extend_schema(summary="Détail d'un poste", responses=PosteSerializer)
    def get(self, request, pk):
        poste = self.get_object(pk)
        if not poste:
            return Response({"detail": "Poste introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(PosteSerializer(poste).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Modifier un poste (RH/Admin)", request=PosteSerializer, responses=PosteSerializer)
    def put(self, request, pk):
        poste = self.get_object(pk)
        if not poste:
            return Response({"detail": "Poste introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PosteSerializer(poste, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Désactiver / Archiver un poste (RH/Admin)", responses=None)
    def delete(self, request, pk):
        poste = self.get_object(pk)
        if not poste:
            return Response({"detail": "Poste introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        poste.est_actif = False
        poste.save()
        return Response({"detail": "Poste désactivé et archivé avec succès."}, status=status.HTTP_200_OK)


class PosteActiverView(APIView):
   
    permission_classes = [IsRhOnlyUserRole]

    @extend_schema(summary="Réactiver un poste archivé (RH/Admin)", responses=PosteSerializer)
    def put(self, request, pk):
        try:
            poste = Poste.objects.get(pk=pk)
        except Poste.DoesNotExist:
            return Response({"detail": "Poste introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        poste.est_actif = True
        poste.save()
        return Response({
            "detail": "Poste réactivé avec succès.",
            "poste": PosteSerializer(poste).data
        }, status=status.HTTP_200_OK)
