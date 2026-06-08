from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Administrateur

@admin.register(Administrateur)
class AdministrateurAdmin(UserAdmin):
    list_display = ('id', 'username', 'nom', 'prenom', 'email', 'telephone', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'nom', 'prenom', 'email', 'telephone')
    ordering = ('nom', 'prenom')

    # 5. Formulaire de modification détaillé par sections
    fieldsets = (
        ("Identifiants de connexion", {
            'fields': ('username', 'password')
        }),
        ("Informations personnelles", {
            'fields': ('nom', 'prenom', 'date_naissance', 'email', 'telephone')
        }),
        ("Statuts et Droits d'accès", {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ("Dates clés", {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # 6. Formulaire simplifié de création d'un NOUVEL Administrateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nom', 'prenom', 'email', 'password', 'telephone'),
        }),
    )

    # 7. Champs techniques verrouillés en lecture seule
    readonly_fields = ('last_login', 'date_joined')
