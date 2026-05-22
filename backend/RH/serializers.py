from rest_framework import serializers
from .models import RH

class RHSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )

    class Meta:
        model  = RH
        fields = ['id', 'email', 'password','nom', 'prenom', 'date_naissance','telephone', 'role', 'is_active']
        read_only_fields = ['role']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = RH(**validated_data)
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
