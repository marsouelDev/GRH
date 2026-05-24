from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from Users.models import RoleEnum
from administrateur.models import Administrateur
from RH.models import RH

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if isinstance(user, Administrateur):
            token = super().get_token(user)
        else:
            token = RefreshToken()
            token['user_id'] = user.pk

        user_role = getattr(user, 'role', None)
        if user_role:
            role_final = user_role.value if hasattr(user_role, 'value') else str(user_role)
        else:
            if isinstance(user, Administrateur): role_final = "ADMIN"
            elif isinstance(user, RH): role_final = "RH"
            else: role_final = "EMPLOYE"

        token['role']   = role_final
        token['email']  = user.email
        token['nom']    = getattr(user, 'nom', '')
        token['prenom'] = getattr(user, 'prenom', '')
        return token

@extend_schema(summary="Authentification / Connexion unique", tags=["Authentification"])
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class AdministrateurSerializer(serializers.ModelSerializer):
    # Permet à la vue de passer le mot de passe généré lors du serializer.save()
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(read_only=True, default="ADMIN")

    class Meta:
        model  = Administrateur
        fields = ['id', 'email', 'password', 'nom', 'prenom', 'date_naissance', 'telephone', 'role', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = Administrateur(**validated_data)
        instance.role = RoleEnum.ADMIN
        instance.is_staff = True
        instance.is_superuser = True
        
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
