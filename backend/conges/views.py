import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Conge
from .serializers import CongeSerializer, RefusSerializer
from .permissions import get_user_role
from notification.models import Notification
from RH.models import RH

logger = logging.getLogger(__name__)


class CongeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Liste des congés (ADMIN/RH tout, Employé uniquement les siens)")
    def get(self, request):
        role = get_user_role(request)

        if role in ('RH', 'ADMIN'):
            qs = Conge.objects.select_related('employe').all()
        elif role == 'EMPLOYE':
            qs = Conge.objects.filter(employe=request.user)
        else:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        statut = request.query_params.get('statut')
        employe_id = request.query_params.get('employe')

        if statut:
            qs = qs.filter(statut=statut)
        if employe_id and role in ('RH', 'ADMIN'):
            qs = qs.filter(employe_id=employe_id)

        return Response(CongeSerializer(qs, many=True).data)

    @extend_schema(summary="Soumettre une demande de congé (RH ou EMPLOYE uniquement)")
    def post(self, request):
        role = get_user_role(request)

        if role == 'ADMIN':
            return Response(
                {"detail": "L'administrateur n'est pas autorisé à créer des demandes."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if role not in ('RH', 'EMPLOYE'):
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CongeSerializer(data=request.data)
        if serializer.is_valid():
            if role == 'EMPLOYE':
                conge = serializer.save(employe=request.user, statut='EN_ATTENTE')
            else:
                conge = serializer.save(statut='EN_ATTENTE')

            try:
                self._envoyer_notifications_rh(conge)
            except Exception as e:
                logger.error(f"❌ Erreur envoi notifications RH : {e}", exc_info=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _envoyer_notifications_rh(self, conge):
        
        logger.info(f"📤 Début envoi notifications RH pour congé #{conge.id}")

        rh_list = RH.objects.filter(is_active=True)
        if not rh_list.exists():
            logger.warning("⚠️ Aucun RH actif trouvé !")
            return

        logger.info(f"✅ {rh_list.count()} RH trouvé(s)")

        emp = conge.employe
        if not emp:
            logger.error("❌ Le congé n'a pas d'employé associé !")
            return

        try:
            type_display = conge.get_type_conge_display()
            duree = conge.calculerDuree()
        except Exception as e:
            logger.error(f"❌ Erreur infos congé : {e}")
            type_display = conge.type_conge
            duree = 0

        message = (
            f"{emp.nom} {emp.prenom} a soumis une demande de congé "
            f"({type_display}) du {conge.date_debut} au {conge.date_fin} "
            f"({duree} jour(s))."
        )
        lien = f"/conges/{conge.id}/"
        titre = f"Nouvelle demande de congé de {emp.nom} {emp.prenom}"

        notifications_objs = []
        for rh in rh_list:
            try:
                notif = Notification(
                    destinataire=rh,
                    type_notif=Notification.TypeNotification.CONGE_SOUMIS,
                    titre=titre,
                    message=message,
                    lien=lien
                )
                notifications_objs.append(notif)
            except Exception as e:
                logger.error(f"❌ Erreur création notif pour RH #{rh.id} : {e}")

        if notifications_objs:
            try:
                created = Notification.objects.bulk_create(notifications_objs)
                logger.info(f"✅ {len(created)} notification(s) RH créée(s)")
            except Exception as e:
                logger.error(f"❌ Erreur bulk_create : {e}", exc_info=True)
                for notif in notifications_objs:
                    try:
                        notif.save()
                    except Exception as e2:
                        logger.error(f"❌ Échec notif RH #{notif.destinataire_id} : {e2}")


class CongeDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Conge.objects.select_related('employe').get(id=id)
        except Conge.DoesNotExist:
            return None

    @extend_schema(summary="Détail d'un congé")
    def get(self, request, id):
        conge = self.get_object(id)
        if not conge:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        role = get_user_role(request)
        if role == 'EMPLOYE' and conge.employe != request.user:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        return Response(CongeSerializer(conge).data)

    def _modifier(self, request, id):
        conge = self.get_object(id)
        if not conge:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        role = get_user_role(request)

        if role == 'EMPLOYE':
            if conge.employe != request.user:
                return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
            if conge.statut != 'EN_ATTENTE':
                return Response(
                    {"detail": "Impossible de modifier un congé déjà traité ou annulé."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif role not in ('RH', 'ADMIN'):
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CongeSerializer(conge, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        return self._modifier(request, id)

    def patch(self, request, id):
        return self._modifier(request, id)

    @extend_schema(summary="Annuler un congé")
    def delete(self, request, id):
        conge = self.get_object(id)
        if not conge:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        role = get_user_role(request)
        if role == 'EMPLOYE' and conge.employe != request.user:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        conge.annuler()
        return Response({"detail": "Le congé a bien été annulé."}, status=status.HTTP_200_OK)


class CongeApprouverView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Approuver un congé (RH uniquement)")
    def put(self, request, id):
        if get_user_role(request) != 'RH':
            return Response({"detail": "Réservé au RH."}, status=status.HTTP_403_FORBIDDEN)

        try:
            conge = Conge.objects.select_related('employe').get(id=id)
        except Conge.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce congé a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)

        commentaire = request.data.get('commentaire', '')

        try:
            conge.approuver(rh=request.user, commentaire=commentaire)
            logger.info(f"✅ Congé #{id} approuvé par {request.user}")
        except Exception as e:
            logger.error(f"❌ Erreur approbation congé #{id} : {e}", exc_info=True)
            return Response({"detail": "Erreur lors de l'approbation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        try:
            if conge.employe:
                Notification.objects.create(
                    destinataire=conge.employe,
                    type_notif=Notification.TypeNotification.CONGE_APPROUVE,
                    titre="Votre congé a été approuvé ✅",
                    message=(
                        f"Votre demande de congé du {conge.date_debut} au {conge.date_fin} "
                        f"a été approuvée. {commentaire}".strip()
                    ),
                    lien=f"/conges/{conge.id}/"
                )
                logger.info(f"✅ Notification d'approbation envoyée à l'employé #{conge.employe.id}")
        except Exception as e:
            logger.error(f"❌ Erreur notif approbation : {e}", exc_info=True)

        return Response({
            "detail": "Congé approuvé avec succès.",
            "conge": CongeSerializer(conge).data
        })


class CongeRefuserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Refuser un congé (RH uniquement)")
    def put(self, request, id):
        if get_user_role(request) != 'RH':
            return Response({"detail": "Réservé au RH."}, status=status.HTTP_403_FORBIDDEN)

        try:
            conge = Conge.objects.select_related('employe').get(id=id)
        except Conge.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if conge.statut != 'EN_ATTENTE':
            return Response({"detail": "Ce congé a déjà été traité."}, status=status.HTTP_400_BAD_REQUEST)

        commentaire = request.data.get('commentaire', '')

        try:
            conge.refuser(rh=request.user, commentaire=commentaire)
            logger.info(f"✅ Congé #{id} refusé par {request.user}")
        except Exception as e:
            logger.error(f"❌ Erreur refus congé #{id} : {e}", exc_info=True)
            return Response({"detail": "Erreur lors du refus."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if conge.employe:
                Notification.objects.create(
                    destinataire=conge.employe,
                    type_notif=Notification.TypeNotification.CONGE_REFUSE,
                    titre="Votre congé a été refusé ❌",
                    message=(
                        f"Votre demande de congé du {conge.date_debut} au {conge.date_fin} "
                        f"a été refusée. Motif : {commentaire}".strip()
                    ),
                    lien=f"/conges/{conge.id}/"
                )
                logger.info(f"✅ Notification de refus envoyée à l'employé #{conge.employe.id}")
        except Exception as e:
            logger.error(f"❌ Erreur notif refus : {e}", exc_info=True)

        return Response({
            "detail": "Congé refusé.",
            "conge": CongeSerializer(conge).data
        })