from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView)
from drf_spectacular.utils import extend_schema_view, extend_schema 
from administrateur.serializers import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Décoration des vues natives de SimpleJWT pour Swagger
TokenRefreshViewDecorated = extend_schema_view(post=extend_schema(summary="Rafraîchir le token d'accès", tags=["Authentification"]))(TokenRefreshView)
TokenBlacklistViewDecorated = extend_schema_view(post=extend_schema(summary="Déconnexion (Blacklist du token)", tags=["Authentification"]))(TokenBlacklistView)

urlpatterns = [
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
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    




