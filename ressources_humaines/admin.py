from django.contrib import admin
from .models import (
    FichePoste, ContratEmploye, MembrePersonnel, Salaire, FichePaie,
    TypeConge, Conge, Absence, SoldeConge
)


@admin.register(FichePoste)
class FichePosteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_contrat', 'salaire_min', 'salaire_max', 'est_active']
    list_filter = ['type_contrat', 'est_active']
    search_fields = ['titre', 'description']


@admin.register(TypeConge)
class TypeCongeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'jours_annuels', 'est_paye', 'est_actif']
    list_filter = ['est_paye', 'est_actif']
    search_fields = ['nom', 'code']


@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ['employe', 'type_conge', 'date_debut', 'date_fin', 'jours', 'statut']
    list_filter = ['statut', 'type_conge', 'date_debut']
    search_fields = ['employe__utilisateur__username', 'motif']
    date_hierarchy = 'date_demande'


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ['employe', 'type_absence', 'date_absence', 'heures', 'est_justifiee', 'statut']
    list_filter = ['type_absence', 'est_justifiee', 'statut']
    search_fields = ['employe__utilisateur__username', 'motif']


@admin.register(SoldeConge)
class SoldeCongeAdmin(admin.ModelAdmin):
    list_display = ['employe', 'type_conge', 'annee', 'jours_restants', 'jours_pris']
    list_filter = ['annee', 'type_conge']
    search_fields = ['employe__utilisateur__username']


@admin.register(ContratEmploye)
class ContratEmployeAdmin(admin.ModelAdmin):
    list_display = ['employe', 'type_contrat', 'date_debut', 'date_fin', 'statut']
    list_filter = ['type_contrat', 'statut']
    search_fields = ['employe__utilisateur__username']


@admin.register(MembrePersonnel)
class MembrePersonnelAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'fonction', 'poste', 'date_embauche', 'est_actif']
    list_filter = ['fonction', 'est_actif']
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name']


@admin.register(Salaire)
class SalaireAdmin(admin.ModelAdmin):
    list_display = ['employe', 'mois', 'annee', 'salaire_brut', 'salaire_net', 'est_paye']
    list_filter = ['annee', 'mois', 'est_paye']
    search_fields = ['employe__utilisateur__username']
    ordering = ['-annee', '-mois']


@admin.register(FichePaie)
class FichePaieAdmin(admin.ModelAdmin):
    list_display = ['salaire', 'periode', 'date_generation']
    search_fields = ['salaire__employe__utilisateur__username']
