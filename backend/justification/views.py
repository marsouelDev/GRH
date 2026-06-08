import logging
import os
from django.db import models
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Justification
from notification.models import Notification
from .serializers import JustificationSerializer, JustificationActionSerializer
from .permissions import IsRhOnlyRole, get_role_str
from RH.models import RH
from employees.models import Employe

logger = logging.getLogger(__name__)


class JustificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        summary="Liste des justifications",
        responses=JustificationSerializer(many=True),
        parameters=[
            OpenApiParameter(name='statut', description="Filtrer par statut", required=False, type=str),
            OpenApiParameter(name='type_justif', description="Filtrer par type", required=False, type=str),
            OpenApiParameter(name='employe', description="Filtrer par ID employé (RH/Admin)", required=False, type=int),
        ]
    )
    def get(self, request):
        role_str = get_role_str(request.user)
        qs = Justification.objects.select_related('employe', 'presence').all()

        if role_str not in ['ADMIN', 'RH']:
            qs = qs.filter(employe=request.user)

        statut = request.query_params.get('statut')
        type_justif = request.query_params.get('type_justif')
        employe_id = request.query_params.get('employe')

        if statut:
            qs = qs.filter(statut=statut)
        if type_justif:
            qs = qs.filter(type_justif=type_justif)
        if employe_id and role_str in ['RH', 'ADMIN']:
            try:
                qs = qs.filter(employe_id=int(employe_id))
            except (ValueError, TypeError):
                return Response(
                    {"detail": "ID employé invalide."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            JustificationSerializer(qs, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(summary="Soumettre une justification")
    def post(self, request):
        role_str = get_role_str(request.user)
        if role_str == 'ADMIN':
            return Response(
                {"detail": "L'administrateur ne dépose pas de justifications."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = JustificationSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            justification = serializer.save(
                employe=request.user if role_str == 'EMPLOYE' else None,
                statut='EN_ATTENTE'
            )
            
            try:
                self._envoyer_notifications_rh(justification)
            except Exception as e:
                logger.error(f"❌ Erreur envoi notifications RH : {e}", exc_info=True)
            
            return Response(
                JustificationSerializer(justification, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

        logger.warning(f"Échec validation justification : {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _envoyer_notifications_rh(self, justification):
        logger.info(f"📤 Début envoi notifications RH pour justification #{justification.id}")
        
        rh_list = RH.objects.filter(is_active=True)
        
        if not rh_list.exists():
            logger.warning("️ Aucun RH actif trouvé !")
            return
        
        logger.info(f"✅ {rh_list.count()} RH trouvé(s)")

        emp = justification.employe
        if not emp:
            logger.error(" La justification n'a pas d'employé associé !")
            return

        try:
            type_display = justification.get_type_justif_display()
            date_presence = justification.presence.date if justification.presence else 'date inconnue'
        except Exception as e:
            logger.error(f"❌ Erreur récupération infos : {e}")
            type_display = justification.type_justif
            date_presence = 'date inconnue'

        message = (
            f"{emp.nom} {emp.prenom} a soumis une justification "
            f"({type_display}) pour le {date_presence}."
        )
        lien = f"/justifications/{justification.id}/"
        titre = f"Nouvelle justification de {emp.nom} {emp.prenom}"

        notifications_objs = []
        for rh in rh_list:
            try:
                notif = Notification(
                    destinataire=rh,
                    type_notif=Notification.TypeNotification.JUSTIF_SOUMISE,
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
                        logger.info(f"✅ Notif créée pour RH #{notif.destinataire_id}")
                    except Exception as e2:
                        logger.error(f"❌ Échec notif RH #{notif.destinataire_id} : {e2}")


class JustificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Justification.objects.select_related('employe', 'presence').get(pk=pk)
        except Justification.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None

    def get(self, request, pk):
        justification = self.get_object(pk)
        if not justification:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        role_str = get_role_str(request.user)
        if role_str == 'EMPLOYE' and justification.employe != request.user:
            return Response({"detail": "Accès interdit."}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            JustificationSerializer(justification, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        justification = self.get_object(pk)
        if not justification:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        role_str = get_role_str(request.user)

        # Vérification des permissions
        if role_str == 'EMPLOYE':
            if justification.employe != request.user:
                return Response(
                    {"detail": "Accès interdit."},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif role_str not in ['RH', 'ADMIN']:
            return Response(
                {"detail": "Permission refusée."},
                status=status.HTTP_403_FORBIDDEN
            )

        if justification.statut != 'EN_ATTENTE':
            return Response(
                {"detail": f"Impossible de supprimer un dossier déjà traité (statut: {justification.statut})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        justif_id = justification.id
        employe = justification.employe
        presence = justification.presence
        document_path = justification.document.path if justification.document else None

        try:
            if justification.document:
                self._supprimer_fichier_physique(document_path)
            
            justification.delete()
            
            logger.info(f"🗑️ Justification #{justif_id} supprimée par {role_str} #{request.user.id}")

            if role_str in ['RH', 'ADMIN'] and employe:
                try:
                    date_str = presence.date if presence else 'date inconnue'
                    Notification.objects.create(
                        destinataire=employe,
                        type_notif=Notification.TypeNotification.JUSTIF_REJETEE,
                        titre="Votre justification a été supprimée 🗑️",
                        message=f"Votre justification du {date_str} a été supprimée par un responsable RH.",
                        lien="/justifications/"
                    )
                except Exception as e:
                    logger.error(f"❌ Erreur notif suppression : {e}", exc_info=True)

            if presence:
                try:
                    if getattr(presence, 'justifie', False):
                        presence.justifie = False
                        presence.save()
                        logger.info(f"ℹ️ Présence #{presence.id} : justifie=False")
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de réinitialiser justifie : {e}")

            return Response(
                {"detail": "Justification supprimée avec succès."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"❌ Erreur suppression #{justif_id} : {e}", exc_info=True)
            return Response(
                {"detail": "Erreur lors de la suppression."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _supprimer_fichier_physique(self, file_path):
        if not file_path:
            return
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Fichier supprimé : {file_path}")
        except Exception as e:
            logger.error(f"❌ Erreur suppression fichier {file_path} : {e}")


class JustificationValiderView(APIView):
    permission_classes = [IsRhOnlyRole]

    @extend_schema(summary="Valider une justification (RH uniquement)")
    def put(self, request, pk):
        try:
            justification = Justification.objects.select_related('employe', 'presence').get(pk=pk)
        except Justification.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "ID invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if justification.statut != 'EN_ATTENTE':
            return Response(
                {"detail": f"Ce dossier a déjà été traité (statut: {justification.statut})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        commentaire = request.data.get('commentaire', '').strip()

        try:
            justification.valider(rh=request.user, commentaire=commentaire)
            logger.info(f"✅ Justification #{pk} validée par {request.user}")
        except Exception as e:
            logger.error(f"❌ Erreur validation #{pk} : {e}", exc_info=True)
            return Response({"detail": "Erreur lors de la validation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  
        try:
            if justification.presence:
                justification.presence.statut = 'PRESENT'
                if hasattr(justification.presence, 'justifie'):
                    justification.presence.justifie = True
                justification.presence.save()
                logger.info(f"✅ Présence #{justification.presence.id} : statut=PRESENT, justifie=True")
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour présence : {e}", exc_info=True)

    
        try:
            if justification.employe:
                date_str = justification.presence.date if justification.presence else 'date inconnue'
                message = f"Votre justification du {date_str} a été acceptée."
                if commentaire:
                    message += f" Commentaire : {commentaire}"
                
                Notification.objects.create(
                    destinataire=justification.employe,
                    type_notif=Notification.TypeNotification.JUSTIF_VALIDEE,
                    titre="Votre justification a été validée ✅",
                    message=message,
                    lien=f"/justifications/{justification.id}/"
                )
                logger.info(f"✅ Notif validation envoyée à l'employé #{justification.employe.id}")
        except Exception as e:
            logger.error(f"❌ Erreur notif validation : {e}", exc_info=True)

        return Response({"detail": "Validée avec succès."}, status=status.HTTP_200_OK)


class JustificationRejeterView(APIView):
    permission_classes = [IsRhOnlyRole]

    @extend_schema(summary="Rejeter une justification (RH uniquement)")
    def put(self, request, pk):
        try:
            justification = Justification.objects.select_related('employe', 'presence').get(pk=pk)
        except Justification.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "ID invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if justification.statut != 'EN_ATTENTE':
            return Response(
                {"detail": f"Ce dossier a déjà été traité (statut: {justification.statut})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        commentaire = request.data.get('commentaire', '').strip()

        try:
            justification.rejeter(rh=request.user, commentaire=commentaire)
            logger.info(f"✅ Justification #{pk} rejetée par {request.user}")
        except Exception as e:
            logger.error(f"❌ Erreur rejet #{pk} : {e}", exc_info=True)
            return Response({"detail": "Erreur lors du rejet."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if justification.presence:
                if hasattr(justification.presence, 'justifie'):
                    justification.presence.justifie = False
                    justification.presence.save()
                    logger.info(f"ℹ️ Présence #{justification.presence.id} : justifie=False")
        except Exception as e:
            logger.error(f" Erreur mise à jour présence : {e}", exc_info=True)

  
        try:
            if justification.employe:
                date_str = justification.presence.date if justification.presence else 'date inconnue'
                message = f"Votre justification du {date_str} a été rejetée."
                if commentaire:
                    message += f" Motif : {commentaire}"
                
                Notification.objects.create(
                    destinataire=justification.employe,
                    type_notif=Notification.TypeNotification.JUSTIF_REJETEE,
                    titre="Votre justification a été rejetée ❌",
                    message=message,
                    lien=f"/justifications/{justification.id}/"
                )
                logger.info(f"✅ Notif rejet envoyée à l'employé #{justification.employe.id}")
        except Exception as e:
            logger.error(f"❌ Erreur notif rejet : {e}", exc_info=True)

        return Response({"detail": "Rejetée."}, status=status.HTTP_200_OK)