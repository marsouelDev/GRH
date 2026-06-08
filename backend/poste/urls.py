from django.urls import path
from .views import PosteListCreateView, PosteDetailUpdateDeleteView, PosteActiverView

urlpatterns = [
    path('postes/', PosteListCreateView.as_view(), name='poste-list-create'),
    path('postes/<int:pk>/', PosteDetailUpdateDeleteView.as_view(), name='poste-detail-update-delete'),
    path('postes/<int:pk>/activer/', PosteActiverView.as_view(), name='poste-activer'),
]
