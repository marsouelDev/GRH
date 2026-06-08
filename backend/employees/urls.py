from django.urls import path
from .views import (EmployeListCreateAPIView,EmployeDetailUpdateDeleteActiveAPIView,EmployeActiverView,DashboardStatsAPIView,EmployeChangeAPIView)


urlpatterns = [

    path('employes/', EmployeListCreateAPIView.as_view(), name='employe-list-create'),
    path('employes/<int:id>/', EmployeDetailUpdateDeleteActiveAPIView.as_view(), name='employe-detail'),
    path('employes/<int:id>/profil/',EmployeChangeAPIView.as_view(),name='employe-change'),
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('employes/<int:id>/active/', EmployeActiverView.as_view(), name='employe-active'),
]