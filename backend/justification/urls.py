from django.urls import path
from .views import (JustificationListCreateView, JustificationDetailView, JustificationValiderView, JustificationRejeterView,)

app_name = 'justification'

urlpatterns = [
    path('justifications/', JustificationListCreateView.as_view(), name='justification-list'),
    path('justifications/<int:pk>/', JustificationDetailView.as_view(), name='justification-detail'),
    path('justifications/<int:pk>/valider/', JustificationValiderView.as_view(), name='justification-valider'),
    path('justifications/<int:pk>/rejeter/', JustificationRejeterView.as_view(), name='justification-rejeter'),
]