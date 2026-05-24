from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils   import extend_schema
from .models import Notification
from .serializers   import (NotificationSerializer,)


class NotificationListView(APIView):
  

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Mes notifications", responses=NotificationSerializer(many=True))
    def get(self, request):
        qs  = Notification.objects.filter(destinataire=request.user)
        lu  = request.query_params.get('lu')
        if lu == 'true':  qs = qs.filter(lu=True)
        if lu == 'false': qs = qs.filter(lu=False)
        return Response(NotificationSerializer(qs, many=True).data)


class NotificationMarquerLuView(APIView):
 
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Marquer notification comme lue", responses=None)
    def put(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, destinataire=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)
        notif.marquerLu()
        return Response({"detail": "Notification marquée comme lue."})


class NotificationToutLireView(APIView):
   
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Tout marquer comme lu", responses=None)
    def put(self, request):
        count = Notification.objects.filter( destinataire=request.user, lu=False).update(lu=True)
        return Response({"detail": f"{count} notification(s) marquée(s) comme lue(s)."})