from django.urls import path
from .views import (
    DashboardStatsView, 
    DashboardEmployesStatsView,
    ClearDashboardCacheView
)

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/employes/', DashboardEmployesStatsView.as_view(), name='dashboard-employes'),
    path('cache/clear/', ClearDashboardCacheView.as_view(), name='clear-cache'),
]