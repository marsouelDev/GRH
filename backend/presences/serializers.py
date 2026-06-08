from rest_framework import serializers
from .models import Presence
from justification.models import Justification


class PresenceSerializer(serializers.ModelSerializer):
 

    employe_nom = serializers.SerializerMethodField(read_only=True)
    statut_label = serializers.SerializerMethodField(read_only=True)
    heures_travaillees = serializers.SerializerMethodField(read_only=True)
    justifie = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Presence
        fields = [
            'id',
            'employe',
            'employe_nom',
            'date',
            'heure_arrivee',
            'heure_depart',
            'statut',
            'statut_label',
            'heures_travaillees',
            'justifie',
        ]
        read_only_fields = ['id', 'date', 'heure_arrivee', 'heure_depart', 'statut']

    
    def get_employe_nom(self, obj: Presence) -> str:
        if not obj.employe:
            return "—"
        prenom = getattr(obj.employe, 'prenom', '')
        nom = getattr(obj.employe, 'nom', '')
        return f"{prenom} {nom}".strip() or str(obj.employe)

    def get_statut_label(self, obj: Presence) -> str:
        return obj.get_statut_display() if hasattr(obj, 'get_statut_display') else obj.statut

    def get_heures_travaillees(self, obj: Presence) -> str | None:
        return obj.calculerHeures() if hasattr(obj, 'calculerHeures') else None

    def get_justifie(self, obj: Presence) -> bool:
      
        return Justification.objects.filter(
            presence=obj,
            statut__in=['EN_ATTENTE', 'VALIDEE']
        ).exists()