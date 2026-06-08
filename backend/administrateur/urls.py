from django.urls import path
from .views import (
    AdministrateurListCreateAPIView,
    AdministrateurDetailUpdateDeleteAPIView,
    AdminChangeProfilAPIView
)

urlpatterns = [
    path('administrateurs/', AdministrateurListCreateAPIView.as_view(), name='admin-list-create'),
    path('administrateurs/<int:id>/', AdministrateurDetailUpdateDeleteAPIView.as_view(), name='admin-detail'),
    path('administrateurs/<int:id>/profil/', AdminChangeProfilAPIView.as_view(), name='admin-change-profil'),
]