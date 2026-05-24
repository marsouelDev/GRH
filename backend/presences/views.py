from datetime import datetime, date, time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Presence
from .serializers import PresenceSerializer
from employees.models import Employe


class PresenceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_superuser or getattr(user, 'role', None) in ['ADMIN', 'RH']:
            presences = Presence.objects.all().order_by('-date')
        else:
            presences = Presence.objects.filter(employe=user).order_by('-date')
            
        serializer = PresenceSerializer(presences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BadgerArriveeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.user, Employe):
            return Response(
                {"detail": "Seuls les employés peuvent badger l'arrivée."},
                status=status.HTTP_403_FORBIDDEN
            )

        employe = request.user
        aujourd_hui = date.today()

        if Presence.objects.filter(employe=employe, date=aujourd_hui).exists():
            return Response(
                {"detail": "Vous avez déjà enregistré votre arrivée pour aujourd'hui."},
                status=status.HTTP_400_BAD_REQUEST
            )

        heure_actuelle = datetime.now().time()
        heure_limite = time(8, 30)
        statut = Presence.Statut.RETARD if heure_actuelle > heure_limite else Presence.Statut.PRESENT

        presence = Presence.objects.create(
            employe=employe,
            heure_arrivee=heure_actuelle,
            statut=statut,
        )

        serializer = PresenceSerializer(presence)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BadgerDepartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Vérifier que c'est bien un Employé
        if not isinstance(request.user, Employe):
            return Response(
                {"detail": "Seuls les employés peuvent badger le départ."},
                status=status.HTTP_403_FORBIDDEN
            )

        employe = request.user
        aujourd_hui = date.today()

        try:
            presence = Presence.objects.get(employe=employe, date=aujourd_hui)
        except Presence.DoesNotExist:
            return Response(
                {"detail": "Impossible de badger le départ sans avoir badgé l'arrivée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if presence.heure_depart:
            return Response(
                {"detail": "Vous avez déjà enregistré votre départ pour aujourd'hui."},
                status=status.HTTP_400_BAD_REQUEST
            )

        presence.heure_depart = datetime.now().time()
        presence.save()

        serializer = PresenceSerializer(presence)
        return Response(serializer.data, status=status.HTTP_200_OK)