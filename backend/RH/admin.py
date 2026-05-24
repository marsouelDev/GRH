from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import RH

@admin.register(RH)
class RHAdmin(UserAdmin):
    
    list_display = ('id', 'username', 'nom', 'prenom', 'email', 'telephone', 'is_active')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'nom', 'prenom', 'email', 'telephone')
    ordering = ('nom', 'prenom')
    fieldsets = (
        ("Identifiants de connexion", {
            'fields': ('username', 'password')
        }),
        ("Informations personnelles", {
            'fields': ('nom', 'prenom', 'date_naissance', 'email', 'telephone')
        }),
        ("Statuts et Droits", {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ("Dates importantes", {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nom', 'prenom', 'email', 'password', 'telephone'),
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
