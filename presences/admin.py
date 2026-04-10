from django.contrib import admin
from .models import Presence, Appel


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'classe', 'date', 'statut', 'justifie']
    list_filter = ['statut', 'date', 'classe']
    search_fields = ['eleve__nom', 'eleve__prenom']


@admin.register(Appel)
class AppelAdmin(admin.ModelAdmin):
    list_display = ['classe', 'date', 'heure_debut', 'professeur', 'matiere']
    list_filter = ['date', 'classe']
