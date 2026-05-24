from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Contrat

@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    list_display = ('id', 'employe', 'type_contrat', 'poste', 'date_debut', 'date_fin', 'salaire_base', 'statut_badge')
    list_filter = ('statut', 'type_contrat', 'date_debut', 'date_fin')
    search_fields = ('employe__nom', 'employe__prenom', 'poste')
    ordering = ('-date_debut',)
    readonly_fields = ('date_creation',)
    fieldsets = (
        ("Affectation", {
            'fields': ('employe', 'poste')
        }),
        ("Détails du Contrat", {
            'fields': ('type_contrat', 'statut', 'salaire_base')
        }),
        ("Dates de Validité", {
            'fields': ('date_debut', 'date_fin', 'date_creation')
        }),
    )
    def statut_badge(self, obj):
        colors = {
            'ACTIF': '#28a745',    # Vert
            'TERMINE': '#dc3545',  # Rouge
            'SUSPENDU': '#ffc107', # Orange
        }
        text_color = '#ffffff' if obj.statut != 'SUSPENDU' else '#000000'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            colors.get(obj.statut, '#6c757d'),
            text_color,
            obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"
