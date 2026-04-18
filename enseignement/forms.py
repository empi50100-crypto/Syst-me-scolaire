from django import forms
from django.db.models import Q
from .models import (
    Classe, Matiere,
    CoefficientMatiere, ContrainteHoraire,
    Attribution, Evaluation,
    Examen, FicheNote, Salle, ProfilProfesseur
)
from core.models import AnneeScolaire


class ClasseForm(forms.ModelForm):
    matieres = forms.ModelMultipleChoiceField(
        queryset=Matiere.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Matières'
    )
    
    class Meta:
        model = Classe
        fields = ['nom', 'niveau', 'serie', 'domaine', 'subdivision', 'capacite', 'professeur_principal', 'annee_scolaire', 'matieres']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Série (Lycée)'}),
            'domaine': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domaine (Université)'}),
            'subdivision': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1, 2, A, B...'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'professeur_principal': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.annee_active = AnneeScolaire.objects.filter(est_active=True).first()
        
        if not self.instance.pk:
            if self.annee_active:
                self.initial['annee_scolaire'] = self.annee_active
        
        if self.instance.pk:
            self.initial['matieres'] = self.instance.matieres.all()


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AttributionForm(forms.ModelForm):
    class Meta:
        model = Attribution
        fields = ['professeur', 'classe', 'matiere', 'annee_scolaire']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
        }


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['eleve', 'matiere', 'classe', 'periode', 'annee_scolaire', 'note', 'coefficient', 'date_eval']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'periode': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_eval': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['nom', 'type_salle', 'capacite', 'etage', 'equipements', 'est_disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_salle': forms.Select(attrs={'class': 'form-select'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'etage': forms.TextInput(attrs={'class': 'form-control'}),
            'equipements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'est_disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CoefficientMatiereForm(forms.ModelForm):
    class Meta:
        model = CoefficientMatiere
        fields = ['classe', 'matiere', 'coefficient']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nom', 'annee_scolaire', 'classe', 'matiere', 'date_examen', 'duree_minutes', 'note_sur', 'coefficient', 'lieu', 'surveillant']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'date_examen': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duree_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'note_sur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
            'lieu': forms.Select(attrs={'class': 'form-select'}),
            'surveillant': forms.Select(attrs={'class': 'form-select'}),
        }


class ContrainteHoraireForm(forms.ModelForm):
    class Meta:
        model = ContrainteHoraire
        fields = ['professeur', 'jour', 'heure_debut', 'heure_fin', 'type_contrainte', 'statut']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-select'}),
            'jour': forms.TextInput(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'type_contrainte': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.TextInput(attrs={'class': 'form-control'}),
        }
