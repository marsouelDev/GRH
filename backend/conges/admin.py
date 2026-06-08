from django.contrib import admin
from django.utils.html import format_html
from .models import Conge

@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'employe', 'type_conge', 'date_debut', 'date_fin', 'duree_jours', 'statut_badge', 'date_demande')
    list_filter = ('statut', 'type_conge', 'date_debut', 'date_demande')
    search_fields = ('employe__nom', 'employe__prenom', 'motif', 'commentaire')
    ordering = ('-date_demande',)
    readonly_fields = ('date_demande', 'duree_jours')

    # 6. Organisation du formulaire de consultation / modification
    fieldsets = (
        ("Demandeur et Type", {
            'fields': ('employe', 'type_conge', 'statut')
        }),
        ("Période du congé", {
            'fields': ('date_debut', 'date_fin', 'duree_jours', 'date_demande')
        }),
        ("Détails et Décision", {
            'fields': ('motif', 'commentaire')
        }),
    )

    # 7. Affichage dynamique de la durée du congé
    def duree_jours(self, obj):
        return f"{obj.calculerDuree()} jour(s)"
    duree_jours.short_description = "Durée"

    # 8. Badge visuel coloré pour le statut de la demande
    def statut_badge(self, obj):
        colors = {
            'EN_ATTENTE': '#ffc107',  # Orange
            'APPROUVE': '#28a745',    # Vert
            'REFUSE': '#dc3545',      # Rouge
            'ANNULE': '#6c757d',      # Gris
        }
        text_colors = {
            'EN_ATTENTE': '#000000',
            'APPROUVE': '#ffffff',
            'REFUSE': '#ffffff',
            'ANNULE': '#ffffff',
        }
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            colors.get(obj.statut, '#6c757d'),
            text_colors.get(obj.statut, '#ffffff'),
            obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"

    # 9. Actions rapides de groupe (Bulk Actions)
    actions = ['approuver_selection', 'refuser_selection', 'annuler_selection']

    def approuver_selection(self, request, queryset):
        for conge in queryset.filter(statut='EN_ATTENTE'):
            conge.approuver()
        self.message_user(request, "Les demandes sélectionnées ont été approuvées.")
    approuver_selection.short_description = "Approuver les demandes de congés"

    def refuser_selection(self, request, queryset):
        for conge in queryset.filter(statut='EN_ATTENTE'):
            conge.refuser(commentaire="Refusé depuis l'administration.")
        self.message_user(request, "Les demandes sélectionnées ont été refusées.")
    refuser_selection.short_description = "Refuser les demandes de congés"

    def annuler_selection(self, request, queryset):
        for conge in queryset:
            conge.annuler()
        self.message_user(request, "Les demandes sélectionnées ont été annulées.")
    annuler_selection.short_description = "Annuler les demandes de congés"
