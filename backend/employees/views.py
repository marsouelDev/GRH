from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .models       import Employe
from .serializers  import EmployeSerializer
from .permissions  import IsRhOrAdmin


class EmployeListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOrAdmin()]

    
    @extend_schema(summary="Liste des employés",responses=EmployeSerializer(many=True),)
    def get(self, request):
        employes   = Employe.objects.all().order_by('id')
        serializer = EmployeSerializer(employes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(summary="Créer un employé",request=EmployeSerializer,responses=EmployeSerializer,)
    def post(self, request):
        serializer = EmployeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeDetailUpdateDeleteAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOrAdmin()]

    def get_object(self, pk):
        try:
            return Employe.objects.get(pk=pk)
        except Employe.DoesNotExist:
            return None

    
    @extend_schema(summary="Détail d'un employé",responses=EmployeSerializer,)
    def get(self, request, pk):
        employe = self.get_object(pk)
        if not employe:
            return Response(
                {"detail": "Employé introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EmployeSerializer(employe)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    @extend_schema(  summary="Modifier un employé",request=EmployeSerializer,responses=EmployeSerializer, )
    def put(self, request, pk):
        employe = self.get_object(pk)
        if not employe:
            return Response(
                {"detail": "Employé introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EmployeSerializer(employe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @extend_schema(summary="Supprimer un employé",responses=None,)
    def delete(self, request, pk):
        employe = self.get_object(pk)
        if not employe:
            return Response(
                {"detail": "Employé introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        employe.delete()
        return Response(
            {"detail": "Employé supprimé avec succès."},
            status=status.HTTP_204_NO_CONTENT
        )