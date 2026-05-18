from django.urls import path
from .views import (EmployeListCreateAPIView,EmployeDetailUpdateDeleteAPIView,)


urlpatterns = [

    path('employes/', EmployeListCreateAPIView.as_view(), name='employe-list-create'),
    path('employes/<int:pk>/', EmployeDetailUpdateDeleteAPIView.as_view(), name='employe-detail'),
]