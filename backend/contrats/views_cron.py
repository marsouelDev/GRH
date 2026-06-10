from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.management import call_command
import os


class CronVerifierContratsView(APIView):
    """Endpoint pour déclencher la vérification des contrats via cron externe"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Vérification du token de sécurité
        auth_header = request.headers.get('Authorization', '')
        expected_token = os.getenv('CRON_SECRET', 'mon-secret-cron-2026')
        
        if not auth_header.startswith('Bearer ') or auth_header.split(' ')[1] != expected_token:
            return Response(
                {"error": "Token invalide"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        jours = int(request.query_params.get('jours', 7))
        
        try:
            call_command('verifier_expiration_contrats', f'--jours={jours}')
            return Response(
                {"success": True, "message": f"Vérification terminée pour {jours} jours"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )