from django.urls import path
from .views import RHDetailUpdateDeleteAPIView,RHListCreateAPIView,RHActiverView


urlpatterns = [
    path('RH/', RHListCreateAPIView.as_view(), name='rh-list-create'),
    path('RH/<int:pk>/', RHDetailUpdateDeleteAPIView.as_view(), name='rh-detail'),
    path('RH/<int:pk>/', RHActiverView.as_view(), name='rh-active'),


]