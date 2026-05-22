from rest_framework import serializers
from .models import  Conge
class CongeSerializer(serializers.ModelSerializer):
 
    employe_nom  = serializers.SerializerMethodField()
    statut_label = serializers.SerializerMethodField()
    type_label   = serializers.SerializerMethodField()
    duree_jours  = serializers.SerializerMethodField()
 
    def get_employe_nom(self, obj):
        return f"{obj.employe.nom} {obj.employe.prenom}"
 
    def get_statut_label(self, obj):
        return obj.get_statut_display()
 
    def get_type_label(self, obj):
        return obj.get_type_conge_display()
 
    def get_duree_jours(self, obj):
        return obj.calculerDuree()
 
    class Meta:
        model  = Conge
        fields = [
            'id',
            'employe',      
            'employe_nom',  
            'type_conge',
            'type_label',
            'date_debut',
            'date_fin',
            'duree_jours',
            'motif',
            'statut',
            'statut_label',
            'date_demande',
            'commentaire',
        ]
        extra_kwargs = {
            'employe':      {'write_only': True},
            'statut':       {'read_only': True},  
            'date_demande': {'read_only': True},
            'commentaire':  {'read_only': True},
        }
 
    def validate(self, data):
        """date_fin doit être >= date_debut."""
        debut = data.get('date_debut')
        fin   = data.get('date_fin')
        if debut and fin and fin < debut:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être après la date de début."}
            )
        return data
 
 
# Serializer pour le commentaire de refus
class RefusSerializer(serializers.Serializer):
    commentaire = serializers.CharField(required=False, allow_blank=True)