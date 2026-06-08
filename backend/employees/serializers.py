from rest_framework import serializers
from Users.models import RoleEnum
from employees.models import Employe

class EmployeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(read_only=True, default="EMPLOYE")

    class Meta:
        model = Employe
        fields = ['id', 'email', 'password', 'nom', 'prenom', 'date_naissance', 'telephone', 'salaire', 'role', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = Employe(**validated_data)
        instance.role = RoleEnum.EMPLOYE
        instance.is_staff = False
        instance.is_superuser = False
        
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ChangeEmployeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employe
        fields = ['id', 'email', 'password', 'nom', 'prenom', 'date_naissance', 'telephone']
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password) 
        instance.save()
        return instance