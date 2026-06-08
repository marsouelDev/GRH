from rest_framework import serializers
from .models import Conge
from employees.models import Employe

class CongeSerializer(serializers.ModelSerializer):
    employe_nom = serializers.SerializerMethodField()
    statut_label = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()
    duree_jours = serializers.SerializerMethodField()
    valide_par_nom = serializers.SerializerMethodField()  

    employe = serializers.PrimaryKeyRelatedField(queryset=Employe.objects.all(),required=False,allow_null=True,write_only=True)

    def get_employe_nom(self, obj):
        if obj.employe:
            return f"{obj.employe.nom} {obj.employe.prenom}".strip()
        return "Employé inconnu"

    def get_statut_label(self, obj):
        return obj.get_statut_display()

    def get_type_label(self, obj):
        return obj.get_type_conge_display()

    def get_duree_jours(self, obj):
        return obj.calculerDuree()

    def get_valide_par_nom(self, obj):
        return obj.get_valide_par_nom()

    class Meta:
        model = Conge
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
            'date_validation',    
            'valide_par_nom',    
        ]
        read_only_fields = [
            'id',
            'employe_nom',
            'type_label',
            'statut_label',
            'duree_jours',
            'date_demande',
            'date_validation',
            'valide_par_nom',
        ]
        extra_kwargs = {
            'date_demande': {'read_only': True},
            'statut': {'read_only': True},  
        }

    def validate(self, data):
        debut = data.get('date_debut')
        fin = data.get('date_fin')
        if debut and fin and fin < debut:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être après la date de début."}
            )
        return data


class RefusSerializer(serializers.Serializer):
    commentaire = serializers.CharField(required=False, allow_blank=True)