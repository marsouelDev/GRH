from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'destinataire', 'type_notif', 'titre', 'lu', 'date_envoi')
    list_filter = ('lu', 'type_notif', 'date_envoi')
    search_fields = ('destinataire__nom', 'destinataire__prenom', 'titre', 'message')
    readonly_fields = ('date_envoi',)
    actions = ['marquer_comme_lu']

    def marquer_comme_lu(self, request, queryset):
        queryset.update(lu=True)
    marquer_comme_lu.short_description = "Marquer les notifications comme lues"
