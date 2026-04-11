from django import forms
from django.forms import formset_factory
from .models import Eleve, EleveInscription, DocumentEleve
from enseignement.models import Classe
from core.models import AnneeScolaire


class DocumentForm(forms.Form):
    type_document = forms.ChoiceField(
        choices=[('', 'Sélectionner')] + list(DocumentEleve.TypeDocument.choices),
        label='Type de document',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fichier = forms.FileField(
        label='Fichier',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'})
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'})
    )


class DocumentFormSetHelper:
    def __init__(self, formset):
        self.formset = formset


DocumentFormSet = formset_factory(DocumentForm, extra=2)


class EleveForm(forms.ModelForm):
    annee_scolaire = forms.ModelChoiceField(
        queryset=AnneeScolaire.objects.filter(est_active=True),
        required=True,
        label='Année scolaire',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Eleve
        fields = ['nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 
                  'adresse', 'telephone_parent', 'email_parent', 'photo', 'observations', 'niveau']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'élève'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom de l\'élève'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de naissance'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse complète'}),
            'telephone_parent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'}),
            'email_parent': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observations sur l\'élève'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['annee_scolaire'].queryset = AnneeScolaire.objects.filter(est_active=True)
        if self.fields['annee_scolaire'].queryset.count() == 1:
            self.fields['annee_scolaire'].initial = self.fields['annee_scolaire'].queryset.first()
        
        if self.instance and self.instance.pk:
            inscription = self.instance.inscriptions.order_by('-annee_scolaire__date_debut').first()
            if inscription:
                self.initial['annee_scolaire'] = inscription.annee_scolaire_id
            
            if self.instance.date_naissance:
                self.initial['date_naissance'] = self.instance.date_naissance
                self.fields['date_naissance'].widget.attrs['value'] = self.instance.date_naissance.strftime('%Y-%m-%d')
            
            if self.instance.photo:
                self.fields['photo'].widget.attrs['data-has-file'] = 'true'
