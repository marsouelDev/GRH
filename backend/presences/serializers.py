from datetime import time, datetime
from rest_framework import serializers
from .models import Presence

class PresenceSerializer(serializers.ModelSerializer):
    employe_nom        = serializers.SerializerMethodField()
    statut_label       = serializers.SerializerMethodField()
    heures_travaillees = serializers.SerializerMethodField()

    class Meta:
        model = Presence
        fields = ['id', 'employe', 'employe_nom', 'date', 'heure_arrivee', 'heure_depart', 'statut', 'statut_label', 'heures_travaillees',]
       
        read_only_fields = ['date', 'heure_arrivee', 'heure_depart', 'statut']

    def get_employe_nom(self, obj):
        return f"{obj.employe.nom} {obj.employe.prenom}"

    def get_statut_label(self, obj):
        return obj.get_statut_display()

    def get_heures_travaillees(self, obj):
        return obj.calculerHeures()
