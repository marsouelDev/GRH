from rest_framework import serializers
from .models import Rapport


class RapportSerializer(serializers.ModelSerializer):
    genere_par_nom = serializers.SerializerMethodField()
    type_label     = serializers.SerializerMethodField()

    class Meta:
        model  = Rapport
        fields = [
            'id', 'titre', 'type_rapport', 'type_label', 'description',
            'genere_par', 'genere_par_nom', 'date_debut', 'date_fin',
            'date_creation', 'donnees',
        ]
        extra_kwargs = {
            'genere_par':    {'write_only': True, 'required': False},
            'date_creation': {'read_only': True},
            'donnees':       {'read_only': True},
        }

    def get_genere_par_nom(self, obj):
        user = obj.genere_par
        if not user:
            return None
        prenom = getattr(user, 'prenom', '') or getattr(user, 'first_name', '')
        nom    = getattr(user, 'nom',    '') or getattr(user, 'last_name',  '')
        if not nom and not prenom:
            return getattr(user, 'username', 'Utilisateur')
        return f"{nom} {prenom}".strip()

    def get_type_label(self, obj):
        try:
            return obj.get_type_rapport_display()
        except AttributeError:
            return obj.type_rapport