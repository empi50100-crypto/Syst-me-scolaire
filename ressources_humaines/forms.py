from django import forms
from .models import FichePoste, MembrePersonnel, Salaire, ContratEmploye
from authentification.models import Utilisateur

class FichePosteForm(forms.ModelForm):
    class Meta:
        model = FichePoste
        fields = ['titre', 'description', 'type_contrat', 'salaire_min', 'salaire_max', 'exigences', 'est_active']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'salaire_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salaire_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'exigences': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MembrePersonnelForm(forms.ModelForm):
    class Meta:
        model = MembrePersonnel
        fields = ['utilisateur', 'fonction', 'poste', 'telephone', 'adresse', 'date_embauche', 'est_actif', 'observations']
        widgets = {
            'utilisateur': forms.Select(attrs={'class': 'form-select'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observations': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].queryset = Utilisateur.objects.filter(is_active=True)


class SalaireForm(forms.ModelForm):
    class Meta:
        model = Salaire
        fields = ['employe', 'mois', 'annee', 'salaire_brut', 'retenue_cnps', 'retenue_irpp', 'autres_retenues', 'date_versement', 'est_paye', 'notes']
        widgets = {
            'employe': forms.Select(attrs={'class': 'form-select'}),
            'mois': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'annee': forms.NumberInput(attrs={'class': 'form-control'}),
            'salaire_brut': forms.NumberInput(attrs={'class': 'form-control'}),
            'retenue_cnps': forms.NumberInput(attrs={'class': 'form-control'}),
            'retenue_irpp': forms.NumberInput(attrs={'class': 'form-control'}),
            'autres_retenues': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_versement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'est_paye': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class ContratEmployeForm(forms.ModelForm):
    class Meta:
        model = ContratEmploye
        fields = ['employe', 'poste', 'type_contrat', 'date_debut', 'date_fin', 'salaire_brut', 'conditions', 'statut']
        widgets = {
            'employe': forms.Select(attrs={'class': 'form-select'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salaire_brut': forms.NumberInput(attrs={'class': 'form-control'}),
            'conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
