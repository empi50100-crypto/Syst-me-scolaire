from django import forms
from django.forms import formset_factory
from .models import Eleve, Inscription, DocumentEleve
from academics.models import Classe
from finances.models import AnneeScolaire


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
    niveau = forms.ChoiceField(
        choices=Eleve.Niveau.choices,
        required=False,
        label='Niveau de classe',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
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
    
    def save(self, commit=True):
        eleve = super().save(commit=False)
        
        # Mettre à jour le niveau de l'élève s'il est sélectionné dans le formulaire
        niveau_selectionne = self.cleaned_data.get('niveau')
        if niveau_selectionne:
            eleve.niveau = niveau_selectionne
            
        if commit:
            eleve.save()
        
        annee = self.cleaned_data.get('annee_scolaire')
        
        # On ne crée l'inscription que si ce n'est pas déjà fait et qu'on a le niveau
        # Remarque: L'inscription proprement dite rattachée à une classe se fera 
        # depuis la vue de création de Classe.
        if annee and eleve.pk and eleve.niveau:
            # On cherche s'il existe une inscription sans classe ou on s'assure juste
            # que l'historique de l'élève est suivi. La vraie affectation sera via ClasseForm.
            pass
        
        return eleve
