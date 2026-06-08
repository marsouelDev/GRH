from django.contrib import admin
from .models import Justification

@admin.register(Justification)
class JustificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'employe', 'type_justif', 'statut', 'date_soumission', 'valide_par')
    list_filter = ('statut', 'type_justif', 'date_soumission')
    search_fields = ('employe__nom', 'employe__prenom', 'motif')
    readonly_fields = ('date_soumission', 'date_validation', 'valide_par')
    actions = ['valider_selection', 'rejeter_selection']

    def valider_selection(self, request, queryset):
        for obj in queryset.filter(statut='EN_ATTENTE'):
            obj.valider(rh=request.user, commentaire="Validé depuis l'administration.")
        self.message_user(request, "Les justifications sélectionnées ont été validées.")
    valider_selection.short_description = "Valider les justifications sélectionnées"

    def rejeter_selection(self, request, queryset):
        for obj in queryset.filter(statut='EN_ATTENTE'):
            obj.rejeter(rh=request.user, commentaire="Rejeté depuis l'administration.")
        self.message_user(request, "Les justifications sélectionnées ont été rejetées.")
    rejeter_selection.short_description = "Rejeter les justifications sélectionnées"
