from rest_framework import serializers
from Users.models import RoleEnum
from RH.models import RH

class RHSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(read_only=True, default="RH")

    class Meta:
        model  = RH
        fields = ['id', 'email', 'password', 'nom', 'prenom', 'date_naissance', 'telephone', 'role', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = RH(**validated_data)
        instance.role = RoleEnum.RH
        instance.is_staff = True
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
