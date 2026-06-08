from django.contrib import admin
from django.utils.html import format_html
from .models import Presence

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    # 1. Configuration des colonnes du tableau principal
    list_display = ('id', 'employe', 'date', 'heure_arrivee', 'heure_depart', 'statut_badge')
    
    # 2. Filtres latéraux pour cibler rapidement les anomalies ou les périodes
    list_filter = ('statut', 'date')
    
    # 3. Barre de recherche (recherche par le nom, prénom ou identifiant de l'employé)
    search_fields = ('employe__nom', 'employe__prenom', 'employe__username')
    
    # 4. Tri par défaut (les journées les plus récentes s'affichent en premier)
    ordering = ('-date',)
    
    # 5. Actions rapides de groupe (Bulk Actions)
    actions = ['regulariser_presence']

    # 6. Badge visuel coloré pour identifier instantanément les statuts
    def statut_badge(self, obj):
        # Utilisation de vos codes couleur pour la charte graphique RH
        colors = {
            'PRESENT': '#28a745',   # Vert
            'RETARD': '#ffc107',    # Orange / Jaune
            'ABSENT': '#ef4458',    # Rouge rosé / Corail vif
        }
        text_colors = {
            'PRESENT': '#ffffff',
            'RETARD': '#000000',
            'ABSENT': '#ffffff',
        }
        # Récupération de la valeur textuelle propre (gère l'attribut du modèle)
        statut_txt = obj.get_statut_display() if hasattr(obj, 'get_statut_display') else str(obj.statut)
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            colors.get(obj.statut, '#6c757d'),
            text_colors.get(obj.statut, '#ffffff'),
            statut_txt
        )
    statut_badge.short_description = "Statut"

    # 7. Action personnalisée pour régulariser les oublis de pointage
    def regulariser_presence(self, request, queryset):
        count = queryset.update(statut='PRESENT')
        self.message_user(request, f"{count} ligne(s) de présence régularisée(s) avec succès.")
    regulariser_presence.short_description = "Régulariser la sélection (Passer à Présent)"
