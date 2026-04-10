from django import forms
from .models import AnneeScolaire, FraisScolaire, Paiement, EcoleCompte, Salaire, CycleConfig, ChargeFixe, ChargeOperationnelle, Personnel
from accounts.models import User


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
        fields = ['type_frais', 'mode_application', 'classe', 'niveau', 'filiere', 'annee_scolaire', 'montant', 'description']
        widgets = {
            'type_frais': forms.Select(attrs={'class': 'form-select'}),
            'mode_application': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'filiere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A1, C, D'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en Fcfa', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe'].required = False
        self.fields['niveau'].required = False
        self.fields['filiere'].required = False


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


class EcoleCompteForm(forms.ModelForm):
    class Meta:
        model = EcoleCompte
        fields = ['date_operation', 'type_operation', 'categorie', 'montant', 'beneficiaire', 'motif', 'personnel']
        widgets = {
            'date_operation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Catégorie'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'beneficiaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bénéficiaire'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motif de l\'opération'}),
        }


class CycleConfigForm(forms.ModelForm):
    class Meta:
        model = CycleConfig
        fields = ['annee_scolaire', 'type_cycle', 'numero', 'date_debut', 'date_fin', 'pourcentage']
        widgets = {
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'type_cycle': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '6'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pourcentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': '0-100'}),
        }


class SalaireSourceForm(forms.Form):
    """Formulaire pour choisir la source du personnel pour le salaire"""
    CHOIX_SOURCE = [
        ('system', 'Utilisateurs du système (Professeurs, Secretary, Comptable...)'),
        ('manual', 'Personnel manuel (Chauffeur, Jardinier, Agent...)'),
    ]
    
    source = forms.ChoiceField(
        choices=CHOIX_SOURCE,
        label="Type de personnel",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_source'})
    )


class SalaireForm(forms.ModelForm):
    class Meta:
        model = Salaire
        fields = ['personnel', 'mois', 'annee', 'salaire_brut', 'retenues', 'date_versement']
        widgets = {
            'personnel': forms.Select(attrs={'class': 'form-select'}),
            'mois': forms.Select(attrs={'class': 'form-select'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année', 'min': '2000', 'max': '2100', 'value': '2026'}),
            'salaire_brut': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salaire brut (laisser vide pour utiliser le salaire du personnel)', 'min': '0'}),
            'retenues': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Retenues', 'min': '0', 'value': '0'}),
            'date_versement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['personnel'].queryset = Personnel.objects.filter(est_actif=True).order_by('nom', 'prenom')
        if not self.instance.pk:
            self.fields['annee'].initial = 2026
            from datetime import datetime
            self.fields['mois'].initial = datetime.now().month
            self.fields['date_versement'].initial = datetime.now().strftime('%Y-%m-%d')


class ChargeFixeForm(forms.ModelForm):
    class Meta:
        model = ChargeFixe
        fields = ['nom', 'type_charge', 'montant', 'periodicite', 'beneficiaire', 'description', 'est_active', 'date_debut', 'date_fin']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la charge'}),
            'type_charge': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en FCFA', 'min': '0'}),
            'periodicite': forms.Select(attrs={'class': 'form-select'}),
            'beneficiaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Propriétaire,SONABEL, ONEA'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ChargeOperationnelleForm(forms.ModelForm):
    class Meta:
        model = ChargeOperationnelle
        fields = ['date_charge', 'type_charge', 'description', 'montant', 'fournisseur', 'reference', 'est_payee', 'date_paiement']
        widgets = {
            'date_charge': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_charge': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description de la charge'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en FCFA', 'min': '0'}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° facture/reçu'}),
            'est_payee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = ['nom', 'prenom', 'fonction', 'telephone', 'adresse', 'salaire_mensuel', 'date_embauche', 'compte_utilisateur', 'est_actif', 'observations']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'fonction': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'salaire_mensuel': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salaire en FCFA', 'min': '0'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'compte_utilisateur': forms.Select(attrs={'class': 'form-select'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compte_utilisateur'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['compte_utilisateur'].required = False
        self.fields['compte_utilisateur'].label = 'Compte utilisateur (optionnel)'
        if not self.instance.pk:
            self.fields['est_actif'].initial = True
