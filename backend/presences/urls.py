from django.urls import path
from .views import PresenceListAPIView, BadgerArriveeAPIView, BadgerDepartAPIView

urlpatterns = [
    path('presences/', PresenceListAPIView.as_view(), name='presence-liste'),
    path('presences/arrivee/', BadgerArriveeAPIView.as_view(), name='badge-arrivee'),
    path('presences/depart/', BadgerDepartAPIView.as_view(), name='badge-depart'),
]
