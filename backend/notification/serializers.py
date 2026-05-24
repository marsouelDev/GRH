from rest_framework import serializers
from .models import  Notification

class NotificationSerializer(serializers.ModelSerializer):
    type_label = serializers.SerializerMethodField()

    def get_type_label(self, obj):
        return obj.getTypeLabel()

    class Meta:
        model  = Notification
        fields = ['id', 'destinataire','type_notif', 'type_label','titre', 'message', 'lien','lu', 'date_envoi',]
        extra_kwargs = {
            'destinataire': {'write_only': True},
            'date_envoi':   {'read_only': True},
        }
