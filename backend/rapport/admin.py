from django.contrib import admin
from .models import Rapport

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_rapport', 'genere_par', 'date_debut', 'date_fin', 'date_creation')
    list_filter = ('type_rapport', 'date_creation')
    search_fields = ('titre', 'description')
    readonly_fields = ('date_creation', 'donnees') 
    actions = ['recalculer_statistiques']

    def recalculer_statistiques(self, request, queryset):
        for rapport in queryset:
            rapport.genererDonnees()
        self.message_user(request, "Les données des rapports sélectionnés ont été recalculées.")
    recalculer_statistiques.short_description = "Recalculer les statistiques (JSON)"
