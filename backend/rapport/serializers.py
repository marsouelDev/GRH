from rest_framework import serializers
from .models import Rapport


class RapportSerializer(serializers.ModelSerializer):
    genere_par_nom  = serializers.SerializerMethodField()
    type_label      = serializers.SerializerMethodField()

    def get_genere_par_nom(self, obj):
        if obj.genere_par:
            return f"{obj.genere_par.nom} {obj.genere_par.prenom}"
        return None

    def get_type_label(self, obj):
        return obj.get_type_rapport_display()

    class Meta:
        model  = Rapport
        fields = ['id', 'titre','type_rapport', 'type_label','description',
                 'genere_par', 'genere_par_nom','date_debut', 'date_fin','date_creation', 'donnees',]
        extra_kwargs = {
            'genere_par':   {'write_only': True},
            'date_creation':{'read_only': True},
            'donnees':      {'read_only': True},
        }