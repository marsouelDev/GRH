from django.urls import path
from .views import ContratListCreateAPIView, ContratDetailUpdateDeleteAPIView, GenererContratPDFView
from .views_cron import CronVerifierContratsView

urlpatterns = [
    path('contrats/', ContratListCreateAPIView.as_view(), name='contrat-list-create'),
    path('contrats/<int:id>/', ContratDetailUpdateDeleteAPIView.as_view(), name='contrat-detail'),
    path('contrats/<int:id>/pdf/', GenererContratPDFView.as_view(), name='contrat-pdf'),
    path('cron/verifier-contrats/', CronVerifierContratsView.as_view(), name='cron-verifier-contrats'),
 
]
