# Dans le fichier serializers.py de l'application 'contrats'
from rest_framework import serializers
from .models import Contrat
from employees.serializers import EmployeSerializer

class ContratSerializer(serializers.ModelSerializer):
    employe_details = EmployeSerializer(source='employe', read_only=True)
    # ✅ C'est ici que l'on déclare poste_intitule
    poste_intitule  = serializers.SerializerMethodField()

    class Meta:
        model  = Contrat
        # En utilisant '__all__', poste_intitule est automatiquement inclus car déclaré au-dessus
        fields = '__all__'
    
    def get_poste_intitule(self, obj):
        if obj.poste:
            return obj.poste.intitule
        return "Aucun poste"

    def validate(self, data):
        type_contrat = data.get('type_contrat')
        date_debut   = data.get('date_debut')
        date_fin     = data.get('date_fin')
        
        if type_contrat in ['CDD', 'STAGE'] and not date_fin:
            raise serializers.ValidationError({"date_fin": "Ce type de contrat exige une date de fin"})
        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError({"date_fin": "La date de fin doit être postérieure à la date de début"})
        return data
