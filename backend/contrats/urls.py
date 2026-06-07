from django.urls import path
from .views import ContratListCreateAPIView, ContratDetailUpdateDeleteAPIView, GenererContratPDFView

urlpatterns = [
    path('contrats/', ContratListCreateAPIView.as_view(), name='contrat-list-create'),
    path('contrats/<int:id>/', ContratDetailUpdateDeleteAPIView.as_view(), name='contrat-detail'),
    path('contrats/<int:id>/pdf/', GenererContratPDFView.as_view(), name='contrat-pdf'), 
]
