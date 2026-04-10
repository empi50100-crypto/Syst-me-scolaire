from django import forms
from django.db.models import Q
from .models import (
    Classe, Matiere, ClasseMatiere,
    CoefficientMatiere, ContrainteHoraire,
    Enseignement, Evaluation,
    Examen, FicheNote, Salle
)
from academics.models import Professeur


class ClasseForm(forms.ModelForm):
    matieres = forms.ModelMultipleChoiceField(
        queryset=Matiere.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Matières'
    )
    eleves = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Élèves'
    )
    
    class Meta:
        model = Classe
        fields = ['nom', 'niveau', 'serie', 'domaine', 'subdivision', 'capacite', 'professeur_principal', 'matieres', 'eleves']
        widgets = {
            'nom': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'serie': forms.Select(attrs={'class': 'form-select', 'empty_option': 'Sélectionner (pour Lycée)'}),
            'domaine': forms.Select(attrs={'class': 'form-select', 'empty_option': 'Sélectionner (pour Université)'}),
            'subdivision': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1, 2, A, B... (laisser vide si une seule classe)'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Nombre d\'élèves"}),
            'professeur_principal': forms.Select(attrs={'class': 'form-select'}),
            'matieres': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'eleves': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from finances.models import AnneeScolaire
        from eleves.models import Eleve
        
        self.annee_active = AnneeScolaire.objects.filter(est_active=True).first()
        
        if self.annee_active:
            from eleves.models import Inscription
            inscribed_in_other_classes = Inscription.objects.filter(
                annee_scolaire=self.annee_active
            )
            if self.instance and self.instance.pk:
                inscribed_in_other_classes = inscribed_in_other_classes.exclude(classe=self.instance)
                
            inscribed_ids = inscribed_in_other_classes.values_list('eleve_id', flat=True)
            self.fields['eleves'].queryset = Eleve.objects.exclude(id__in=inscribed_ids).order_by('nom', 'prenom')
        
        if self.instance.pk:
            selected_matieres = self.instance.matieres.all()
            self.initial['matieres'] = selected_matieres
            
            from eleves.models import Inscription
            inscribed_eleves = Inscription.objects.filter(
                classe=self.instance,
                annee_scolaire=self.annee_active
            ).values_list('eleve_id', flat=True) if self.annee_active else []
            self.initial['eleves'] = list(inscribed_eleves)
    
    def get_selected_matiere_ids(self):
        if self.instance.pk:
            return list(self.instance.matieres.values_list('id', flat=True))
        return []
    
    def get_selected_eleve_ids(self):
        if self.instance.pk and self.annee_active:
            from eleves.models import Inscription
            return list(Inscription.objects.filter(
                classe=self.instance,
                annee_scolaire=self.annee_active
            ).values_list('eleve_id', flat=True))
        return []
    
    def clean_annee_scolaire(self):
        if self.annee_active:
            return self.annee_active
        raise forms.ValidationError("Aucune année scolaire active. Veuillez créer une année scolaire d'abord.")
    
    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        niveau = cleaned_data.get('niveau')
        serie = cleaned_data.get('serie') or ''
        domaine = cleaned_data.get('domaine') or ''
        subdivision = cleaned_data.get('subdivision', '').strip()
        
        if self.annee_active and nom and niveau:
            existing = Classe.objects.filter(
                nom=nom,
                serie=serie,
                domaine=domaine,
                annee_scolaire=self.annee_active
            )
            
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if subdivision:
                existing = existing.filter(subdivision=subdivision)
            
            if existing.exists():
                if subdivision:
                    raise forms.ValidationError({
                        'subdivision': f'La classe {nom}-{subdivision} existe déjà pour cette année scolaire.'
                    })
                else:
                    raise forms.ValidationError({
                        'subdivision': 'Une classe avec ce nom existe déjà. Veuillez indiquer une subdivision (ex: 1, 2, A, B...).'
                    })
            
            if not subdivision:
                count_without_sub = Classe.objects.filter(
                    nom=nom,
                    serie=serie,
                    domaine=domaine,
                    subdivision='',
                    annee_scolaire=self.annee_active
                ).count()
                
                if self.instance.pk:
                    count_without_sub = Classe.objects.filter(
                        nom=nom,
                        serie=serie,
                        domaine=domaine,
                        subdivision='',
                        annee_scolaire=self.annee_active
                    ).exclude(pk=self.instance.pk).count()
                
                if count_without_sub > 0:
                    raise forms.ValidationError({
                        'subdivision': 'Une classe avec ce nom existe déjà. Veuillez indiquer une subdivision (ex: 1, 2, A, B...).'
                    })
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.annee_scolaire_id and self.annee_active:
            instance.annee_scolaire = self.annee_active
        if instance.subdivision is None:
            instance.subdivision = ''
        if commit:
            instance.save()
            
            matieres_selected = self.cleaned_data.get('matieres', [])
            for matiere in matieres_selected:
                cm, created = ClasseMatiere.objects.get_or_create(
                    classe=instance,
                    matiere=matiere,
                    defaults={'coefficient': matiere.coefficient}
                )
            
            if self.instance.pk:
                existing_ids = set(instance.matieres.values_list('id', flat=True))
                selected_ids = set(m.id for m in matieres_selected)
                to_remove = existing_ids - selected_ids
                instance.matieres.remove(*to_remove)
            
            from eleves.models import Inscription
            eleves_selected = self.cleaned_data.get('eleves', [])
            
            for eleve in eleves_selected:
                Inscription.objects.get_or_create(
                    eleve=eleve,
                    classe=instance,
                    annee_scolaire=self.annee_active
                )
            
            if self.instance.pk:
                existing_inscriptions = set(Inscription.objects.filter(
                    classe=instance,
                    annee_scolaire=self.annee_active
                ).values_list('eleve_id', flat=True))
                selected_eleve_ids = set(e.id for e in eleves_selected)
                to_remove_ids = existing_inscriptions - selected_eleve_ids
                Inscription.objects.filter(
                    classe=instance,
                    annee_scolaire=self.annee_active,
                    eleve_id__in=to_remove_ids
                ).delete()
        
        return instance


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom', 'coefficient']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la matière (ex: Mathématiques, Français...)'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Coefficient (ex: 1, 2, 3...)', 'min': '1', 'value': '1'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        coefficient = cleaned_data.get('coefficient')
        
        if nom and coefficient:
            existing = Matiere.objects.filter(nom__iexact=nom, coefficient=coefficient)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f'La matière "{nom}" avec coefficient {coefficient} existe déjà.')
        
        return cleaned_data


class EnseignementForm(forms.ModelForm):
    class Meta:
        model = Enseignement
        fields = ['professeur', 'classe', 'matiere', 'annee_scolaire']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from finances.models import AnneeScolaire
        annee = AnneeScolaire.objects.filter(est_active=True).first()
        if annee:
            self.fields['annee_scolaire'].initial = annee
            self.fields['annee_scolaire'].widget.attrs['readonly'] = True


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['eleve', 'matiere', 'type_eval', 'titre', 'date_eval', 'note', 'coefficient', 'observations', 'annee_scolaire']
        widgets = {
            'date_eval': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'type_eval': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Note sur 20', 'step': '0.01', 'min': '0', 'max': '20'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Coefficient', 'min': '1'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observations...'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from finances.models import AnneeScolaire
        annee = AnneeScolaire.objects.filter(est_active=True).first()
        if annee:
            self.fields['annee_scolaire'].initial = annee


class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['nom', 'type_salle', 'capacite', 'etage', 'equipements', 'est_disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la salle'}),
            'type_salle': forms.Select(attrs={'class': 'form-select'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacité'}),
            'etage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: RDC, 1er étage'}),
            'equipements': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Équipements disponibles', 'rows': 3}),
            'est_disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CoefficientMatiereForm(forms.ModelForm):
    class Meta:
        model = CoefficientMatiere
        fields = ['classe', 'matiere', 'coefficient']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from finances.models import AnneeScolaire
        annee = AnneeScolaire.objects.filter(est_active=True).first()
        if annee:
            self.fields['classe'].queryset = Classe.objects.filter(annee_scolaire=annee)
    
    def clean(self):
        cleaned_data = super().clean()
        classe = cleaned_data.get('classe')
        matiere = cleaned_data.get('matiere')
        
        if classe and matiere:
            existing = CoefficientMatiere.objects.filter(classe=classe, matiere=matiere)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f'Le coefficient pour {matiere.nom} existe déjà pour {classe.nom}.')
        
        return cleaned_data


class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nom', 'type_examen', 'annee_scolaire', 'classe', 'matiere', 'date_examen', 
                  'duree_minutes', 'note_sur', 'coefficient', 'lieu', 'surveillant', 'instructions']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'examen"}),
            'type_examen': forms.Select(attrs={'class': 'form-select'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'date_examen': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duree_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Durée en minutes'}),
            'note_sur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Note sur'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'lieu': forms.Select(attrs={'class': 'form-select'}),
            'surveillant': forms.Select(attrs={'class': 'form-select'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from finances.models import AnneeScolaire
        annee = AnneeScolaire.objects.filter(est_active=True).first()
        if annee:
            self.fields['annee_scolaire'].initial = annee
            self.fields['annee_scolaire'].widget.attrs['readonly'] = True
            self.fields['classe'].queryset = Classe.objects.filter(annee_scolaire=annee)


class ContrainteHoraireForm(forms.ModelForm):
    class Meta:
        model = ContrainteHoraire
        fields = ['professeur', 'jour', 'heure_debut', 'heure_fin', 'type_contrainte', 'motif', 'est_recurrent', 'date_fin']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-select'}),
            'jour': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'type_contrainte': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'est_recurrent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ProfesseurForm(forms.ModelForm):
    class Meta:
        model = Professeur
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