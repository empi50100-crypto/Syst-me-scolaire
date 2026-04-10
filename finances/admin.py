from django.contrib import admin
from .models import (
    AnneeScolaire, FraisScolaire, Paiement, EcoleCompte, Salaire, Rappel, CycleConfig,
    Facture, LigneFacture, BourseRemise, EleveBourse, CategorieDepense, RapportFinancier
)


@admin.register(CycleConfig)
class CycleConfigAdmin(admin.ModelAdmin):
    list_display = ['annee_scolaire', 'type_cycle', 'numero', 'date_debut', 'date_fin', 'pourcentage']
    list_filter = ['annee_scolaire', 'type_cycle']


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'date_debut', 'date_fin', 'est_active']
    list_filter = ['est_active']


@admin.register(FraisScolaire)
class FraisScolaireAdmin(admin.ModelAdmin):
    list_display = ['type_frais', 'montant', 'description']
    list_filter = ['type_frais']


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'frais', 'date_paiement', 'montant', 'mode_paiement']
    list_filter = ['date_paiement', 'mode_paiement']


@admin.register(EcoleCompte)
class EcoleCompteAdmin(admin.ModelAdmin):
    list_display = ['date_operation', 'type_operation', 'categorie', 'montant']
    list_filter = ['type_operation', 'date_operation']


@admin.register(Salaire)
class SalaireAdmin(admin.ModelAdmin):
    list_display = ['personnel', 'mois', 'annee', 'salaire_brut', 'salaire_net', 'est_paye']
    list_filter = ['est_paye', 'annee']


@admin.register(Rappel)
class RappelAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'type_rappel', 'date_echeance', 'montant_due', 'statut']
    list_filter = ['statut', 'type_rappel']


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero_facture', 'eleve', 'date_facture', 'montant_total', 'montant_paye', 'statut']
    list_filter = ['statut', 'date_facture']
    search_fields = ['numero_facture', 'eleve__nom', 'eleve__prenom']
    inlines = [LigneFactureInline]


@admin.register(BourseRemise)
class BourseRemiseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_remise', 'pourcentage', 'est_active']
    list_filter = ['type_remise', 'est_active']


@admin.register(EleveBourse)
class EleveBourseAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'bourse', 'annee_scolaire', 'pourcentage_accorde', 'est_active']
    list_filter = ['annee_scolaire', 'est_active']
    search_fields = ['eleve__nom', 'eleve__prenom']


@admin.register(CategorieDepense)
class CategorieDepenseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'est_active']
    list_filter = ['est_active']


@admin.register(RapportFinancier)
class RapportFinancierAdmin(admin.ModelAdmin):
    list_display = ['type_rapport', 'annee_scolaire', 'date_debut', 'date_fin', 'solde']
    list_filter = ['type_rapport', 'annee_scolaire']
    readonly_fields = ['date_generation']
