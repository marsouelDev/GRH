from django.urls import path
from .views import AdministrateurListCreateAPIView, AdministrateurDetailUodateDeleteAPIView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('administrateurs/', AdministrateurListCreateAPIView.as_view(), name='admin-list-create'),
    path('administrateurs/<int:pk>/', AdministrateurDetailUodateDeleteAPIView.as_view(), name='admin-detail'),
    path("login/", TokenObtainPairView.as_view(),name="Token_Obtain_Pair"),
    path("refresh/",TokenRefreshView.as_view(),name="Token_Refresh"),
]
