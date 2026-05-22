from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils   import extend_schema
 
from .models      import  Conge
from .serializers import CongeSerializer, RefusSerializer
from .permissions import IsRhUserRole

class CongeListCreateView(APIView):
 
    permission_classes = [IsAuthenticated]
 
    @extend_schema(summary="Liste des congés",responses=CongeSerializer(many=True),)
    def get(self, request):
        
        if request.user.role in ['RH', 'ADMIN']:
            qs = Conge.objects.all()
        else:
            qs = Conge.objects.filter(employe=request.user)
 
        statut     = request.query_params.get('statut')
        employe_id = request.query_params.get('employe')
        type_conge = request.query_params.get('type_conge')
 
        if statut:     qs = qs.filter(statut=statut)
        if employe_id: qs = qs.filter(employe_id=employe_id)
        if type_conge: qs = qs.filter(type_conge=type_conge)
 
        return Response(CongeSerializer(qs, many=True).data)
 
    @extend_schema(summary="Soumettre une demande de congé",request=CongeSerializer,responses=CongeSerializer,)
    def post(self, request):
        serializer = CongeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 

class CongeDetailUpdateDeleteView(APIView):
 
    permission_classes = [IsAuthenticated]
 
    def get_object(self, id):
        try:    return Conge.objects.get(id=id)
        except: return None
 
    @extend_schema(summary="Détail congé", responses=CongeSerializer)
    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Congé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CongeSerializer(obj).data)
 
    @extend_schema(summary="Modifier congé", request=CongeSerializer, responses=CongeSerializer)
    def put(self, request, pk):
        conge = self.get_object(pk)
        if not conge:
            return Response({"detail": "Congé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if conge.statut != 'EN_ATTENTE':
            return Response(
                {"detail": "Impossible de modifier un congé déjà traité."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CongeSerializer(conge, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    @extend_schema(summary="Annuler congé", responses=None)
    def delete(self, request, id):
        conge = self.get_object(id)
        if not conge:
            return Response({"detail": "Congé introuvable."}, status=status.HTTP_404_NOT_FOUND)
        conge.annuler()
        return Response({"detail": "Congé annulé."}, status=status.HTTP_200_OK)
 

class CongeApprouverView(APIView):
 
    def get_permissions(self):
        return [IsRhUserRole()]
 
    @extend_schema(summary="Approuver un congé", responses=CongeSerializer)
    def put(self, request, id):
        try:
            conge = Conge.objects.get(id=id)
        except Conge.DoesNotExist:
            return Response({"detail": "Congé introuvable."}, status=status.HTTP_404_NOT_FOUND)
 
        if conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce congé a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)
 
        conge.approuver()
        return Response({"detail":  "Congé approuvé avec succès.","conge":  CongeSerializer(conge).data,})
 
class CongeRefuserView(APIView):
 
    def get_permissions(self):
        return [IsRhUserRole()]
 
    @extend_schema(summary="Refuser un congé",request=RefusSerializer,responses=CongeSerializer,)
    def put(self, request, id):
        try:
            conge = Conge.objects.get(id=id)
        except Conge.DoesNotExist:
            return Response({"detail": "Congé introuvable."}, status=status.HTTP_404_NOT_FOUND)
 
        if conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce congé a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)
 
        commentaire = request.data.get('commentaire', '')
        conge.refuser(commentaire=commentaire)
        return Response({"detail": "Congé refusé.","conge":  CongeSerializer(conge).data,})