from django.urls import path
from .views import (CongeListCreateView,CongeDetailUpdateDeleteView,CongeApprouverView,CongeRefuserView,)

urlpatterns = [
  
    path('conges/', CongeListCreateView.as_view(), name='conge-list-create'),
    path('conges/<int:id>/', CongeDetailUpdateDeleteView.as_view(), name='conge-detail'),
    path('conges/<int:id>/approuver/', CongeApprouverView.as_view(), name='conge-approuver'),
    path('conges/<int:id>/refuser/', CongeRefuserView.as_view(), name='conge-refuser'),
]
