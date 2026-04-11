from django import forms
from finances.models import (
    FraisScolaire, Paiement, OperationCaisse, RappelPaiement,
    ChargeFixe, ChargeOperationnelle, Facture, LigneFacture, BourseRemise,
    EleveBourse, CategorieDepense, RapportFinancier
)
from core.models import AnneeScolaire, Cycle
from authentification.models import Utilisateur
from ressources_humaines.models import MembrePersonnel, Salaire


class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['libelle', 'date_debut', 'date_fin', 'est_active', 'type_cycle_actif']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2025-2026'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type_cycle_actif': forms.Select(attrs={'class': 'form-select'}),
        }


class FraisScolaireForm(forms.ModelForm):
    class Meta:
        model = FraisScolaire
        fields = ['type_frais', 'mode_application', 'classe', 'niveau', 'annee_scolaire', 'montant', 'description']
        widgets = {
            'type_frais': forms.Select(attrs={'class': 'form-select'}),
            'mode_application': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en Fcfa', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe'].required = False
        self.fields['niveau'].required = False


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['eleve', 'frais', 'date_paiement', 'montant', 'mode_paiement', 'reference', 'observations']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'frais': forms.Select(attrs={'class': 'form-select'}),
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° reçu, transaction'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class OperationCaisseForm(forms.ModelForm):
    class Meta:
        model = OperationCaisse
        fields = ['date_operation', 'type_operation', 'categorie', 'montant', 'beneficiaire', 'motif', 'personnel']
        widgets = {
            'date_operation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Catégorie'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'beneficiaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bénéficiaire'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motif de l\'opération'}),
            'personnel': forms.Select(attrs={'class': 'form-select'}),
        }


class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ['annee_scolaire', 'type_cycle', 'numero', 'date_debut', 'date_fin', 'pourcentage']
        widgets = {
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'type_cycle': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pourcentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ChargeFixeForm(forms.ModelForm):
    class Meta:
        model = ChargeFixe
        fields = ['nom', 'type_charge', 'montant', 'periodicite', 'est_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_charge': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'periodicite': forms.TextInput(attrs={'class': 'form-control'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChargeOperationnelleForm(forms.ModelForm):
    class Meta:
        model = ChargeOperationnelle
        fields = ['date_charge', 'type_charge', 'description', 'montant', 'fournisseur', 'est_payee']
        widgets = {
            'date_charge': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_charge': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'est_payee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
