from django.urls import path
from .views import RHDetailUpdateDeleteAPIView,RHListCreateAPIView,RHActiverView, RhChangeAPIView


urlpatterns = [
    path('RH/', RHListCreateAPIView.as_view(), name='rh-list-create'),
    path('RH/<int:pk>/', RHDetailUpdateDeleteAPIView.as_view(), name='rh-detail'),
    path('RH/<int:pk>/activer/', RHActiverView.as_view(), name='rh-active'),
    path('RH/<int:pk>/profil/', RhChangeAPIView.as_view(), name='rh-change'),
]