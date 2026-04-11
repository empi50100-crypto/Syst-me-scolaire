from django import forms
from django.db.models import Q
from .models import (
    Classe, Matiere, ClasseMatiere,
    CoefficientMatiere, ContrainteHoraire,
    Enseignement, Evaluation,
    Examen, FicheNote, Salle
)
from enseignement.models importProfesseur


classProfesseurForm(forms.ModelForm):
    class Meta:
        model =Professeur
        fields = ['user', 'nom', 'prenom', 'email', 'telephone', 'date_embauche', 'statut', 'salaire_base']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select', 'empty_option': 'Sélectionner un utilisateur'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'salaire_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salaire de base', 'step': '0.01'}),
        }
