from django.contrib import admin
from .models import (
    FraisScolaire, Paiement, OperationCaisse, RappelPaiement,
    Facture, LigneFacture, BourseRemise, EleveBourse, CategorieDepense, RapportFinancier
)


@admin.register(FraisScolaire)
class FraisScolaireAdmin(admin.ModelAdmin):
    list_display = ['type_frais', 'montant', 'description']
    list_filter = ['type_frais']


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'frais', 'date_paiement', 'montant', 'mode_paiement']
    list_filter = ['date_paiement', 'mode_paiement']


@admin.register(OperationCaisse)
class OperationCaisseAdmin(admin.ModelAdmin):
    list_display = ['date_operation', 'type_operation', 'categorie', 'montant']
    list_filter = ['type_operation', 'date_operation']


@admin.register(RappelPaiement)
class RappelPaiementAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'date_echeance', 'montant_due', 'statut']
    list_filter = ['statut']


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero_facture', 'eleve', 'date_facture', 'montant_total', 'statut']
    list_filter = ['statut', 'date_facture']
    search_fields = ['numero_facture', 'eleve__nom', 'eleve__prenom']
    inlines = [LigneFactureInline]


@admin.register(BourseRemise)
class BourseRemiseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pourcentage', 'est_active']
    list_filter = ['est_active']


@admin.register(EleveBourse)
class EleveBourseAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'bourse', 'annee_scolaire']
    list_filter = ['annee_scolaire']
    search_fields = ['eleve__nom', 'eleve__prenom']


@admin.register(CategorieDepense)
class CategorieDepenseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'est_active']
    list_filter = ['est_active']


@admin.register(RapportFinancier)
class RapportFinancierAdmin(admin.ModelAdmin):
    list_display = ['annee_scolaire', 'date_debut', 'date_fin', 'solde']
    list_filter = ['annee_scolaire']
