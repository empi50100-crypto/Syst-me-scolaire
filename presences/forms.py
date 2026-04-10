from django import forms
from .models import Presence, Appel


class PresenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ['eleve', 'classe', 'date', 'statut', 'motif_absence', 'justifie']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'motif_absence': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motif d\'absence'}),
            'justifie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AppelForm(forms.ModelForm):
    class Meta:
        model = Appel
        fields = ['classe', 'date', 'heure_debut', 'heure_fin', 'professeur', 'matiere']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'professeur': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
        }
