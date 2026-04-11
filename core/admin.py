from django.contrib import admin
from .models import AnneeScolaire, Cycle, NiveauScolaire, PeriodeEvaluation, ConfigurationEtablissement


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'date_debut', 'date_fin', 'est_active']
    list_filter = ['est_active']
    search_fields = ['libelle']


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'annee_scolaire', 'type_cycle', 'numero']
    list_filter = ['type_cycle', 'annee_scolaire']
    search_fields = ['annee_scolaire__libelle']


@admin.register(NiveauScolaire)
class NiveauScolaireAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'niveau', 'ordre']
    list_filter = []
    search_fields = ['libelle', 'niveau']
    ordering = ['ordre']


@admin.register(PeriodeEvaluation)
class PeriodeEvaluationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'debut', 'fin', 'numero']
    list_filter = ['type_periode', 'annee_scolaire']
    search_fields = ['annee_scolaire__libelle']


@admin.register(ConfigurationEtablissement)
class ConfigurationEtablissementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'directeur', 'telephone', 'email']