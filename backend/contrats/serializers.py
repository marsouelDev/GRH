from rest_framework import serializers
from .models import Contrat
from employees.serializers import EmployeSerializer

class ContratSerializer(serializers.ModelSerializer):
    employe_details = EmployeSerializer(source='employe',read_only=True)
    class Meta:
        model = Contrat
        fields = '__all__'
    
    def validate(self, data):
        type_contrat = data.get('type_contrat')
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')
        
        if type_contrat in ['CDD','STAGE'] and not date_fin:
            raise serializers.ValidationError({"date_fin":"Ce type de contrat exige une date de fin"})
        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError({"date_fin":"La date de fin doit etre posterieur a la date de debut"})
        return data
    