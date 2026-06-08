from datetime import date, datetime, timedelta, time
from typing import Optional
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Presence
from .serializers import PresenceSerializer
from employees.models import Employe
from RH.models import RH
from administrateur.models import Administrateur

logger = logging.getLogger(__name__)


def _get_role(user) -> str:
    role = getattr(user, 'role', None)
    if role is None:
        return ''
    return role.value if hasattr(role, 'value') else str(role)


def _est_manager(user) -> bool:
    role = _get_role(user).upper()
    return (
        user.is_superuser
        or role in ('ADMIN', 'RH')
        or isinstance(user, (RH, Administrateur))
    )


def _est_employe(user) -> bool:
    if isinstance(user, Employe):
        return True
    if _get_role(user).upper() == 'EMPLOYE':
        return True
    return Employe.objects.filter(pk=user.pk).exists()


def _get_employe(user) -> Optional[Employe]:
    if isinstance(user, Employe):
        return user
    try:
        return Employe.objects.get(pk=user.pk)
    except Employe.DoesNotExist:
        return None


def _get_jours_ouvres_last_30() -> list:
    aujourd_hui = date.today()
    jours_ouvres = []
    i = 0
    
    while len(jours_ouvres) < 30:
        jour = aujourd_hui - timedelta(days=i)
        if jour.weekday() not in (5, 6):  # 5=samedi, 6=dimanche
            jours_ouvres.append(jour)
        i += 1
    
    return jours_ouvres


def _enregistrer_absences_manquantes(employe: Employe) -> None:
    try:
        jours_ouvres = _get_jours_ouvres_last_30()

        dates_existantes = set(
            Presence.objects.filter(
                employe=employe,
                date__in=jours_ouvres,
            ).values_list('date', flat=True)
        )

        absences_a_creer = [
            Presence(
                employe=employe,
                date=jour,
                heure_arrivee=None,
                heure_depart=None,
                statut='ABSENT',
            )
            for jour in jours_ouvres
            if jour not in dates_existantes
        ]

        if absences_a_creer:
            Presence.objects.bulk_create(absences_a_creer, ignore_conflicts=True)
            logger.info(f" {len(absences_a_creer)} absence(s) créée(s) pour {employe}")
            
    except Exception as e:
        logger.error(f"❌ Erreur _enregistrer_absences_manquantes: {e}", exc_info=True)
        pass


class PresenceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Liste des présences sur 30 jours ouvrés",
        description="Retourne l'historique des présences avec génération automatique des absences manquantes.",
        responses={200: PresenceSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='employe',
                description="ID de l'employé à filtrer (réservé aux RH/Admin)",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get(self, request):
        try:
            user = request.user
            jours_ouvres = _get_jours_ouvres_last_30()

            if _est_manager(user):
                employe_id = request.query_params.get('employe')

                if employe_id:
                    try:
                        cible = Employe.objects.get(pk=employe_id)
                    except Employe.DoesNotExist:
                        return Response(
                            {"detail": "Employé introuvable."},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    _enregistrer_absences_manquantes(cible)
                    presences = Presence.objects.filter(
                        employe=cible,
                        date__in=jours_ouvres,
                    ).order_by('-date')
                else:
                    presences = Presence.objects.filter(
                        date__in=jours_ouvres,
                    ).select_related('employe').order_by('-date', 'employe__nom')

                return Response(
                    PresenceSerializer(presences, many=True, context={'request': request}).data,
                    status=status.HTTP_200_OK,
                )

            if _est_employe(user):
                employe = _get_employe(user)
                if employe is None:
                    return Response(
                        {"detail": "Profil employé introuvable."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                _enregistrer_absences_manquantes(employe)

                presences = Presence.objects.filter(
                    employe=employe,
                    date__in=jours_ouvres,
                ).order_by('-date')

                return Response(
                    PresenceSerializer(presences, many=True, context={'request': request}).data,
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"detail": "Accès refusé."},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        except Exception as e:
            logger.error(f" Erreur GET /presences/: {e}", exc_info=True)
            return Response(
                {"detail": f"Erreur serveur : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BadgerArriveeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Enregistrer l'arrivée",
        description="Badge l'arrivée de l'employé authentifié.",
        responses={
            201: PresenceSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    )
    def post(self, request):
        try:
            if not _est_employe(request.user):
                return Response(
                    {"detail": "Seuls les employés peuvent badger l'arrivée."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            employe = _get_employe(request.user)
            if employe is None:
                return Response(
                    {"detail": "Profil employé introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            aujourd_hui = date.today()

            if aujourd_hui.weekday() in (5, 6):
                return Response(
                    {"detail": "Impossible de badger un samedi ou un dimanche."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            heure_actuelle = datetime.now().time()

            if heure_actuelle > time(17, 0):
                statut_value = "ABSENT"
            elif heure_actuelle > time(8, 30):
                statut_value = "RETARD"
            else:
                statut_value = "PRESENT"

            presence, created = Presence.objects.get_or_create(
                employe=employe,
                date=aujourd_hui,
                defaults={
                    'heure_arrivee': heure_actuelle,
                    'heure_depart': None,
                    'statut': statut_value,
                },
            )

            if not created:
                if presence.heure_arrivee:
                    return Response(
                        {"detail": "Vous avez déjà enregistré votre arrivée pour aujourd'hui."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                presence.heure_arrivee = heure_actuelle
                presence.statut = statut_value
                presence.save(update_fields=['heure_arrivee', 'statut'])

            return Response(
                PresenceSerializer(presence, context={'request': request}).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
            
        except Exception as e:
            logger.error(f" Erreur POST /presences/arrivee/: {e}", exc_info=True)
            return Response(
                {"detail": f"Erreur serveur : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BadgerDepartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Enregistrer le départ",
        description="Badge le départ de l'employé authentifié.",
        responses={
            200: PresenceSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    )
    def post(self, request):
        try:
            if not _est_employe(request.user):
                return Response(
                    {"detail": "Seuls les employés peuvent badger le départ."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            employe = _get_employe(request.user)
            if employe is None:
                return Response(
                    {"detail": "Profil employé introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            aujourd_hui = date.today()

            if aujourd_hui.weekday() in (5, 6):
                return Response(
                    {"detail": "Impossible de badger un samedi ou un dimanche."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                presence = Presence.objects.get(employe=employe, date=aujourd_hui)
            except Presence.DoesNotExist:
                return Response(
                    {"detail": "Impossible de badger le départ sans avoir badgé l'arrivée."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not presence.heure_arrivee:
                return Response(
                    {"detail": "Veuillez d'abord enregistrer votre arrivée."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if presence.heure_depart:
                return Response(
                    {"detail": "Vous avez déjà enregistré votre départ pour aujourd'hui."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            presence.heure_depart = datetime.now().time()
            presence.save(update_fields=['heure_depart'])

            return Response(
                PresenceSerializer(presence, context={'request': request}).data,
                status=status.HTTP_200_OK,
            )
            
        except Exception as e:
            logger.error(f" Erreur POST /presences/depart/: {e}", exc_info=True)
            return Response(
                {"detail": f"Erreur serveur : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )