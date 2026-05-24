from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
 
from .models import Justification
from notification.models import Notification
from .serializers import JustificationSerializer, JustificationActionSerializer
from .permissions import IsRhOnlyRole, IsRhOrAdminRole, get_role_str


class JustificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Liste des justifications (RH/Admin voient tout, Employé voit les siennes)",
        responses=JustificationSerializer(many=True),
        parameters=[
            OpenApiParameter(name='statut', description="Filtrer par statut", required=False, type=str),
            OpenApiParameter(name='type_justif', description="Filtrer par type", required=False, type=str),
            OpenApiParameter(name='employe', description="Filtrer par ID employé (RH/Admin uniquement)", required=False, type=int),
        ]
    )
    def get(self, request):
        role_str = get_role_str(request.user)

        if role_str in ['RH', 'ADMIN']:
            qs = Justification.objects.select_related('employe', 'presence').all()
        else:
            qs = Justification.objects.select_related('employe', 'presence').filter(employe=request.user)

        statut = request.query_params.get('statut')
        type_justif = request.query_params.get('type_justif')
        employe_id = request.query_params.get('employe')

        if statut: qs = qs.filter(statut=statut)
        if type_justif: qs = qs.filter(type_justif=type_justif)
        if employe_id and role_str in ['RH', 'ADMIN']:
            qs = qs.filter(employe_id=employe_id)

        return Response(JustificationSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Soumettre une justification (RH ou Employé)", request=JustificationSerializer, responses=JustificationSerializer)
    def post(self, request):
        role_str = get_role_str(request.user)
        if role_str == 'ADMIN':
            return Response({"detail": "L'administrateur ne dépose pas de justifications."}, status=status.HTTP_403_FORBIDDEN)

        serializer = JustificationSerializer(data=request.data)
        if serializer.is_valid():
            if role_str == 'EMPLOYE':
                justification = serializer.save(employe=request.user, statut='EN_ATTENTE')
            else:
                justification = serializer.save()

            from employees.models import Employe as EmployeModel
            rh_list = EmployeModel.objects.filter(role='RH', is_active=True)
            emp = justification.employe
            for rh in rh_list:
                Notification.envoyer(
                    destinataire=rh,
                    type_notif=Notification.TypeNotification.JUSTIF_SOUMISE,
                    titre=f"Nouvelle justification de {emp.nom} {emp.prenom}",
                    message=f"{emp.nom} {emp.prenom} a soumis une justification "
                            f"({justification.get_type_justif_display()}) "
                            f"pour le {justification.presence.date}.",
                    lien=f"/justifications/{justification.id}/"
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JustificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try: return Justification.objects.get(pk=pk)
        except Justification.DoesNotExist: return None

    @extend_schema(summary="Détail d'une justification")
    def get(self, request, pk):
        justification = self.get_object(pk)
        if not justification:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        if get_role_str(request.user) == 'EMPLOYE' and justification.employe != request.user:
            return Response({"detail": "Accès interdit."}, status=status.HTTP_403_FORBIDDEN)
            
        return Response(JustificationSerializer(justification).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Supprimer une justification (En attente uniquement)")
    def delete(self, request, pk):
        justification = self.get_object(pk)
        if not justification:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
            
        if get_role_str(request.user) == 'EMPLOYE' and justification.employe != request.user:
            return Response({"detail": "Accès interdit."}, status=status.HTTP_403_FORBIDDEN)
            
        if justification.statut != 'EN_ATTENTE':
            return Response({"detail": "Impossible de supprimer un dossier déjà traité."}, status=status.HTTP_400_BAD_REQUEST)
            
        justification.delete()
        return Response({"detail": "Justification supprimée."}, status=status.HTTP_204_NO_CONTENT)


class JustificationValiderView(APIView):
    permission_classes = [IsRhOnlyRole] 

    @extend_schema(summary="Valider une justification (RH uniquement)", request=JustificationActionSerializer, responses=JustificationSerializer)
    def put(self, request, pk):
        try: justification = Justification.objects.get(pk=pk)
        except Justification.DoesNotExist: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if justification.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce dossier a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)

        commentaire = request.data.get('commentaire', '')
        justification.valider(rh=request.user, commentaire=commentaire)

        Notification.envoyer(
            destinataire=justification.employe,
            type_notif=Notification.TypeNotification.JUSTIF_VALIDEE,
            titre="Votre justification a été validée",
            message=f"Votre justification du {justification.presence.date} a été acceptée. {commentaire}",
            lien=f"/justifications/{justification.id}/"
        )
        return Response({"detail": "Validée avec succès.", "justification": JustificationSerializer(justification).data}, status=status.HTTP_200_OK)


class JustificationRejeterView(APIView):
    permission_classes = [IsRhOnlyRole()] 

    @extend_schema(summary="Rejeter une justification (RH uniquement)", request=JustificationActionSerializer, responses=JustificationSerializer)
    def put(self, request, pk):
        try: justification = Justification.objects.get(pk=pk)
        except Justification.DoesNotExist: return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if justification.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce dossier a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)

        commentaire = request.data.get('commentaire', '')
        justification.rejeter(rh=request.user, commentaire=commentaire)

        Notification.envoyer(
            destinataire=justification.employe,
            type_notif=Notification.TypeNotification.JUSTIF_REJETEE,
            titre="Votre justification a été rejetée",
            message=f"Votre justification du {justification.presence.date} a été rejetée. Motif : {commentaire}",
            lien=f"/justifications/{justification.id}/"
        )
        return Response({"detail": "Rejetée.", "justification": JustificationSerializer(justification).data}, status=status.HTTP_200_OK)
