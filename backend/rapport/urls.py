from django.urls import path
from .views import (RapportListCreateView, RapportDetailView, RapportRegeneView, ExportRapportExcelView, ExportRapportPdfView)

urlpatterns = [
    path('rapports/', RapportListCreateView.as_view(), name='rapport-list-create'),
    path('rapports/<int:pk>/', RapportDetailView.as_view(), name='rapport-detail'),
    path('rapports/<int:pk>/regenerer/', RapportRegeneView.as_view(), name='rapport-regenerer'),
     path('rapports/<int:pk>/export/excel/', ExportRapportExcelView.as_view(), name='rapport-export-excel'),
    path('rapports/<int:pk>/export/pdf/', ExportRapportPdfView.as_view(), name='rapport-export-pdf'),
]
