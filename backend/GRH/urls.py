from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView)
from drf_spectacular.utils import extend_schema_view, extend_schema 
from administrateur.serializers import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from django.conf import settings
from django.conf.urls.static import static

# Décoration des vues natives de SimpleJWT pour Swagger
TokenRefreshViewDecorated = extend_schema_view(post=extend_schema(summary="Rafraîchir le token d'accès", tags=["Authentification"]))(TokenRefreshView)
TokenBlacklistViewDecorated = extend_schema_view(post=extend_schema(summary="Déconnexion (Blacklist du token)", tags=["Authentification"]))(TokenBlacklistView)

def health_check(request):
  
    return JsonResponse({
        'status': 'ok',
        'message': 'API Workflow RH - Gestion des Ressources Humaines',
        'version': '1.0.0',
        'docs': '/api/docs/'
    })


urlpatterns = [
 
    path('', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/login/', MyTokenObtainPairView.as_view(), name='login'),
    path('api/logout/', TokenBlacklistViewDecorated.as_view(), name='token_blacklist'),
    path('api/refresh/', TokenRefreshViewDecorated.as_view(), name='refresh'),
    path('', include('employees.urls')),
    path('', include('administrateur.urls')),
    path('', include('RH.urls')),
    path('', include('presences.urls')),
    path('', include('conges.urls')),
    path('', include('contrats.urls')),
    path('', include('justification.urls')),
    path('', include('poste.urls')),
    path('', include('notification.urls')),
    path('', include('rapport.urls')),
    path('', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)