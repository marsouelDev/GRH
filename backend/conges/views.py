from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import Conge
from .serializers import CongeSerializer, RefusSerializer
from .permissions import IsAdminUserRole, IsRhUserRole, IsEmployeUserRole, get_user_role


class CongeListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole | IsRhUserRole | IsEmployeUserRole]
 
    @extend_schema(summary="Liste des congés (ADMIN/RH tout, Employé uniquement les siens)")
    def get(self, request):
        role_str = get_user_role(request)

        if role_str in ['RH', 'ADMIN']:
            qs = Conge.objects.select_related('employe').all()
        else:
            qs = Conge.objects.filter(employe=request.user)
 
        statut = request.query_params.get('statut')
        employe_id = request.query_params.get('employe')
        if statut: qs = qs.filter(statut=statut)
        if employe_id and role_str in ['RH', 'ADMIN']: qs = qs.filter(employe_id=employe_id)
 
        return Response(CongeSerializer(qs, many=True).data)
 
    @extend_schema(summary="Soumettre une demande de congé (RH ou EMPLOYE uniquement)")
    def post(self, request):
        role_str = get_user_role(request)
        if role_str == 'ADMIN':
            return Response({"detail": "L'administrateur n'est pas autorisé à créer de demandes."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CongeSerializer(data=request.data)
        if serializer.is_valid():
            if role_str == 'EMPLOYE':
                serializer.save(employe=request.user, statut='EN_ATTENTE')
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class CongeDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole | IsRhUserRole | IsEmployeUserRole]
 
    def get_object(self, id):
        try: return Conge.objects.get(id=id)
        except Conge.DoesNotExist: return None
 
    @extend_schema(summary="Détail d'un congé")
    def get(self, request, id):
        conge = self.get_object(id)
        if not conge: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification de la permission d'objet pour l'employé
        self.check_object_permissions(request, conge)
        return Response(CongeSerializer(conge).data)
 
    @extend_schema(summary="Modifier un congé (RH tout, Employé uniquement si EN_ATTENTE)")
    def p_u_t_o_r_p_a_t_c_h(self, request, id): 
        conge = self.get_object(id)
        if not conge: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        self.check_object_permissions(request, conge)
        role_str = get_user_role(request)

        if role_str == 'EMPLOYE' and conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Impossible de modifier un congé déjà traité ou annulé."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CongeSerializer(conge, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id): return self.p_u_t_o_r_p_a_t_c_h(request, id)
    def patch(self, request, id): return self.p_u_t_o_r_p_a_t_c_h(request, id)
 
    @extend_schema(summary="Supprimer / Annuler un congé (RH ou l'Employé propriétaire)")
    def delete(self, request, id):
        conge = self.get_object(id)
        if not conge: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        self.check_object_permissions(request, conge)
        
        # Appel de la méthode d'annulation du modèle pour garder l'historique propre
        conge.annuler()
        return Response({"detail": "Le congé a bien été annulé."}, status=status.HTTP_200_OK)


class CongeApprouverView(APIView):
    permission_classes = [IsAuthenticated, IsRhUserRole]
 
    @extend_schema(summary="Approuver un congé (RH uniquement)")
    def put(self, request, id):
        try: conge = Conge.objects.get(id=id)
        except Conge.DoesNotExist: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
 
        if conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce congé a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)
 
        conge.approuver()
        return Response({"detail": "Congé approuvé avec succès.", "conge": CongeSerializer(conge).data})
 

class CongeRefuserView(APIView):
    permission_classes = [IsAuthenticated, IsRhUserRole]
 
    @extend_schema(summary="Refuser un congé (RH uniquement)")
    def put(self, request, id):
        try: conge = Conge.objects.get(id=id)
        except Conge.DoesNotExist: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
 
        if conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce congé a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)
 
        commentaire = request.data.get('commentaire', '')
        conge.refuser(commentaire=commentaire)
        return Response({"detail": "Congé refusé.", "conge": CongeSerializer(conge).data})
