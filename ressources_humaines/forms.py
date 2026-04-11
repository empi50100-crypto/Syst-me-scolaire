from django import forms
from .models import FichePoste, MembrePersonnel, Salaire, ContratEmploye
from authentification.models import User


class FichePosteForm(forms.ModelForm):
    class Meta:
        model = FichePoste
        fields = ['titre', 'description', 'type_contrat', 'salaire_min', 'salaire_max', 'exigences', 'est_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'exigences': forms.Textarea(attrs={'rows': 3}),
        }


class MembrePersonnelForm(forms.ModelForm):
    class Meta:
        model = MembrePersonnel
        fields = ['utilisateur', 'fonction', 'poste', 'telephone', 'adresse', 'date_embauche', 'est_actif', 'observations']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
            'observations': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].queryset = User.objects.filter(is_active=True)


class SalaireForm(forms.ModelForm):
    class Meta:
        model = Salaire
        fields = ['employe', 'mois', 'annee', 'salaire_brut', 'retenue_cnps', 'retenue_irpp', 'autres_retenues', 'date_versement', 'est_paye', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class ContratEmployeForm(forms.ModelForm):
    class Meta:
        model = ContratEmploye
        fields = ['employe', 'poste', 'type_contrat', 'date_debut', 'date_fin', 'salaire_brut', 'conditions', 'statut']
        widgets = {
            'conditions': forms.Textarea(attrs={'rows': 2}),
        }