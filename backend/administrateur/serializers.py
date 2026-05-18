from rest_framework import serializers
from .models import Administrateur
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

       #  insère le rôle de l'employé directement dans le jeton JWT
        token['role'] = user.role 
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class AdministrateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = Administrateur
        fields = ['id', 'username', 'email', 'password', 'nom', 'prenom', 'date_naissance', 'telephone', 'role', 'is_active']
        read_only_fields = ['role']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Utilise create_user de Django si hérité d'AbstractUser, sinon gère le mot de passe manuellement
        instance = Administrateur(**validated_data)
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
