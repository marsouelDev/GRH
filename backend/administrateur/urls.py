from django.urls import path
from .views import AdministrateurListCreateAPIView, AdministrateurDetailUodateDeleteAPIView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from administrateur.serializers import MyTokenObtainPairView 

urlpatterns = [
    path('administrateurs/', AdministrateurListCreateAPIView.as_view(), name='admin-list-create'),
    path('administrateurs/<int:pk>/', AdministrateurDetailUodateDeleteAPIView.as_view(), name='admin-detail'),

]
