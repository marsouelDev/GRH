from rest_framework import serializers
from .models import Poste

class PosteSerializer(serializers.ModelSerializer):
    nombre_occupants = serializers.SerializerMethodField()
    vacant   = serializers.SerializerMethodField()
    niveau_label     = serializers.SerializerMethodField()

    def get_nombre_occupants(self, obj):
        return obj.getNombreOccupants()

    def get_vacant(self, obj):
        return obj.estVacant()

    def get_niveau_label(self, obj):
        return obj.get_niveau_hierarchie_display()

    class Meta:
        model  = Poste
        fields = ['id', 'intitule', 'description','niveau_hierarchie', 'niveau_label','salaire_min', 'salaire_max',
                  'est_actif', 'date_creation','nombre_occupants', 'vacant', ]
