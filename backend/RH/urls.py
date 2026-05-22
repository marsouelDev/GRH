from django.urls import path
from .views import RHDetailUpdateDeleteAPIView,RHListCreateAPIView


urlpatterns = [
    path('RH/', RHListCreateAPIView.as_view(), name='admin-list-create'),
    path('RH/<int:pk>/', RHDetailUpdateDeleteAPIView.as_view(), name='admin-detail'),

]