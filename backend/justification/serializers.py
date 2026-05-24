from rest_framework import serializers
from .models import  Justification
class JustificationSerializer(serializers.ModelSerializer):
    employe_nom  = serializers.SerializerMethodField()
    statut_label = serializers.SerializerMethodField()
    type_label  = serializers.SerializerMethodField()
    valide_par_nom = serializers.SerializerMethodField()
    presence_date  = serializers.SerializerMethodField()

    def get_employe_nom(self, obj):
        return f"{obj.employe.nom} {obj.employe.prenom}"

    def get_statut_label(self, obj):
        return obj.get_statut_display()

    def get_type_label(self, obj):
        return obj.get_type_justif_display()

    def get_valide_par_nom(self, obj):
        if obj.valide_par:
            return f"{obj.valide_par.nom} {obj.valide_par.prenom}"
        return None

    def get_presence_date(self, obj):
        return str(obj.presence.date)

    class Meta:
        model  = Justification
        fields = ['id','presence', 'presence_date','employe', 'employe_nom','type_justif', 'type_label','motif', 'document',
                  'statut', 'statut_label','date_soumission','commentaire_rh','valide_par', 'valide_par_nom','date_validation',
                 ]
        extra_kwargs = {
            'employe':        {'write_only': True},
            'valide_par':     {'read_only': True},
            'statut':         {'read_only': True},
            'date_validation':{'read_only': True},
            'date_soumission':{'read_only': True},
            'commentaire_rh': {'read_only': True},
        }

    def validate(self, data):
        
        presence = data.get('presence')
        employe  = data.get('employe')
        if presence and employe and presence.employe != employe:
            raise serializers.ValidationError(
                "La présence ne correspond pas à l'employé."
            )
        return data
    
class JustificationActionSerializer(serializers.Serializer):
    commentaire = serializers.CharField(required=False, allow_blank=True)