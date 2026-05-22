from rest_framework import serializers
from .models import Employe


class EmployeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employe
        fields = [
            "id", "email", "password", "is_active", "date_joined",
            "nom", "prenom", "date_naissance", "telephone", "salaire",
        ]
        extra_kwargs = {
            "password":    {"write_only": True, "required": False},
            "date_joined": {"read_only": True},
            "is_active":   {"read_only": True},
        }

    def create(self, validated_data):
       
        password = validated_data.pop("password", None)
        employe = Employe(**validated_data)
        if password:
            employe.set_password(password)  
        employe.save()
        return employe

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance