from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Mes notifications", responses=NotificationSerializer(many=True))
    def get(self, request):
        user_content_type = ContentType.objects.get_for_model(request.user)
        
        qs = Notification.objects.filter(
            content_type=user_content_type, 
            object_id=request.user.pk
        )
        
        lu = request.query_params.get('lu')
        if lu == 'true':  
            qs = qs.filter(lu=True)
        elif lu == 'false': 
            qs = qs.filter(lu=False)
            
        return Response(NotificationSerializer(qs, many=True).data)


class NotificationMarquerLuView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Marquer notification comme lue", responses=None)
    def put(self, request, pk):
        user_content_type = ContentType.objects.get_for_model(request.user)
        
        try:
            notif = Notification.objects.get(
                pk=pk, 
                content_type=user_content_type, 
                object_id=request.user.pk
            )
        except Notification.DoesNotExist:
            return Response({"detail": "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)
            
        notif.marquerLu()
        return Response({"detail": "Notification marquée comme lue."})


class NotificationToutLireView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Tout marquer comme lu", responses=None)
    def put(self, request):
        user_content_type = ContentType.objects.get_for_model(request.user)
        
        count = Notification.objects.filter(
            content_type=user_content_type, 
            object_id=request.user.pk, 
            lu=False
        ).update(lu=True)
        
        return Response({"detail": f"{count} notification(s) marquée(s) comme lue(s)."})