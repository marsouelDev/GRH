from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from .models import Administrateur


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        # Si l'utilisateur est un Administrateur → comportement normal (OutstandingToken OK)
        if isinstance(user, Administrateur):
            token = super().get_token(user)
        else:
            # Employe / RH → on crée le token SANS passer par OutstandingToken
            token = RefreshToken()
            token['user_id'] = user.pk

        # Champs personnalisés injectés dans le token
        token['role']   = getattr(user, 'role', 'EMPLOYE')
        token['email']  = user.email
        token['nom']    = getattr(user, 'nom', '')
        token['prenom'] = getattr(user, 'prenom', '')

        return token


@extend_schema(
    summary="Authentification / Connexion unique",
    description="Permet aux Administrateurs, RH et Employés de se connecter pour obtenir un Token JWT.",
    tags=["Authentification"]
)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class AdministrateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )

    class Meta:
        model  = Administrateur
        fields = ['id', 'email', 'password', 'nom', 'prenom', 'date_naissance', 'telephone', 'role', 'is_active']
        read_only_fields = ['role']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
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