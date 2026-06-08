from django.contrib import admin
from .models import Poste

@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ('intitule', 'niveau_hierarchie', 'salaire_min', 'salaire_max', 'est_actif', 'nombre_occupants', 'vacant')
    list_filter = ('niveau_hierarchie', 'est_actif', 'date_creation')
    search_fields = ('intitule', 'description')
    readonly_fields = ('date_creation',)
    filter_horizontal = ('employes',)  # Interface plus propre pour associer les employés

    def nombre_occupants(self, obj):
        return obj.getNombreOccupants()
    nombre_occupants.short_description = "Occupants"

    def vacant(self, obj):
        return "Oui" if obj.estVacant() else "Non"
    vacant.short_description = "Vacant ?"
