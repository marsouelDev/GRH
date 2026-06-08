from rest_framework import serializers
from .models import Justification
from django.conf import settings


class JustificationSerializer(serializers.ModelSerializer):
    
    employe_nom = serializers.SerializerMethodField(read_only=True)
    statut_label = serializers.SerializerMethodField(read_only=True)
    type_label = serializers.SerializerMethodField(read_only=True)
    valide_par_nom = serializers.SerializerMethodField(read_only=True)
    presence_date = serializers.SerializerMethodField(read_only=True)
    document_url = serializers.SerializerMethodField(read_only=True)

    commentaire = serializers.CharField(
        source='commentaire_rh',
        read_only=True,
        allow_blank=True,
        allow_null=True
    )

    motif = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=5,
        max_length=500,
        help_text="Motif de la justification (5-500 caractères)"
    )

    class Meta:
        model = Justification
        fields = [
            'id',
            'presence',
            'presence_date',
            'employe',
            'employe_nom',
            'type_justif',
            'type_label',
            'motif',
            'document',        
            'document_url',    
            'statut',
            'statut_label',
            'date_soumission',
            'commentaire',
            'valide_par_nom',
            'date_validation',
        ]
        read_only_fields = [
            'id',
            'presence_date',
            'employe_nom',
            'type_label',
            'statut',
            'statut_label',
            'date_soumission',
            'commentaire',
            'valide_par_nom',
            'date_validation',
            'document_url',    
        ]
        extra_kwargs = {
            'employe': {'write_only': True, 'required': False, 'allow_null': True},
            'presence': {'required': True},
            'type_justif': {'required': True},
            'document': {'required': False, 'allow_null': True}, 
        }

    def get_employe_nom(self, obj: Justification) -> str | None:
        if not obj.employe:
            return None
        prenom = getattr(obj.employe, 'prenom', '')
        nom = getattr(obj.employe, 'nom', '')
        return f"{nom} {prenom}".strip() or None

    def get_statut_label(self, obj: Justification) -> str:
        if hasattr(obj, 'get_statut_display'):
            return obj.get_statut_display()
        return obj.statut if obj.statut else 'INCONNU'

    def get_type_label(self, obj: Justification) -> str:
        if hasattr(obj, 'get_type_justif_display'):
            return obj.get_type_justif_display()
        return obj.type_justif if obj.type_justif else 'INCONNU'

    def get_valide_par_nom(self, obj: Justification) -> str | None:
        return obj.get_valide_par_nom()

    def get_presence_date(self, obj):
        if obj.presence:
            return str(obj.presence.date)
        return None

    def get_document_url(self, obj: Justification) -> str | None:
        if not obj.document:
            return None
        
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.document.url)
        
        return f"{settings.MEDIA_URL.rstrip('/')}{obj.document.url}"

    def validate_presence(self, value):
        if not value:
            raise serializers.ValidationError("Veuillez sélectionner une présence valide.")

        if value.statut not in ('ABSENT', 'RETARD'):
            raise serializers.ValidationError(
                "Seules les absences et les retards peuvent être justifiés."
            )

        if Justification.objects.filter(presence=value).exists():
            raise serializers.ValidationError(
                "Cette présence a déjà une justification."
            )

        return value

    def validate_type_justif(self, value):
        if value not in ('RETARD', 'ABSENCE'):
            raise serializers.ValidationError(
                "Le type doit être soit 'RETARD' soit 'ABSENCE'."
            )
        return value

    def validate(self, data):
        presence = data.get('presence')
        request = self.context.get('request')

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if presence and presence.employe != request.user:
                raise serializers.ValidationError(
                    {"presence": "Cette présence ne vous appartient pas."}
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['employe'] = request.user
            validated_data['statut'] = 'EN_ATTENTE'

        return super().create(validated_data)


class JustificationActionSerializer(serializers.Serializer):
    commentaire = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500,
        help_text="Commentaire optionnel pour l'employé (max 500 caractères)"
    )

    def validate_commentaire(self, value):
        if value:
            return value.strip()
        return value