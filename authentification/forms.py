from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm as DjangoUserCreationForm
from .models import Utilisateur, PermissionPersonnalisee, Module
from enseignement.models import Matiere


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})


class UserRegistrationForm(DjangoUserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'})
    )
    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    telephone = forms.CharField(
        label='Téléphone',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'})
    )
    role = forms.ChoiceField(
        label='Service / Fonction',
        choices=[('', 'Sélectionner votre service')] + list(Utilisateur.Role.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    adresse = forms.CharField(
        label='Adresse',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Votre adresse complète'})
    )
    matiere = forms.ModelChoiceField(
        label='Matière enseignée',
        queryset=Matiere.objects.all().order_by('nom'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='-- Sélectionner une matière --'
    )

    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'adresse', 'role', 'matiere')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})

        # N'afficher qu'un seul nom de matière (sans doublons de coefficients)
        from django.db.models import Min
        ids_uniques = Matiere.objects.values('nom').annotate(id_min=Min('id')).values_list('id_min', flat=True)
        self.fields['matiere'].queryset = Matiere.objects.filter(id__in=ids_uniques).order_by('nom')
        self.fields['matiere'].label_from_instance = lambda obj: obj.nom
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError('Veuillez sélectionner votre service/fonction.')
        
        from .models import RoleQuota
        if not RoleQuota.can_create_user(role):
            limit = RoleQuota.get_limit(role)
            current = RoleQuota.get_current_count(role)
            role_display = dict(Utilisateur.Role.choices).get(role, role)
            raise forms.ValidationError(f'Limite atteinte pour le rôle "{role_display}". Maximum: {limit}, Actuel: {current}')
        
        return role
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.est_approuve = False
        user.is_active = True
        # Sauvegarder les champs personnalisés
        user.telephone = self.cleaned_data.get('telephone', '')
        user.adresse = self.cleaned_data.get('adresse', '')
        user.matiere = self.cleaned_data.get('matiere')
        if commit:
            user.save()
        return user


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}))
    password2 = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'}))
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'adresse', 'matiere', 'is_active', 'est_approuve']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'role': forms.Select(attrs={'class': 'form-select', 'id': 'id_role'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'matiere': forms.Select(attrs={'class': 'form-select', 'id': 'id_matiere'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_approuve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Afficher uniquement le nom de la matière (sans coefficient)
        from django.db.models import Min
        from enseignement.models import Matiere
        ids_uniques = Matiere.objects.values('nom').annotate(id_min=Min('id')).values_list('id_min', flat=True)
        queryset = Matiere.objects.filter(id__in=ids_uniques).order_by('nom')
        
        # Si l'utilisateur a déjà une matière assignée qui n'est pas dans le queryset filtré,
        # on l'ajoute pour éviter les problèmes d'affichage
        if self.instance and self.instance.pk and self.instance.matiere_id:
            if not queryset.filter(id=self.instance.matiere_id).exists():
                matiere_actuelle = Matiere.objects.filter(id=self.instance.matiere_id).first()
                if matiere_actuelle:
                    queryset = list(queryset) + [matiere_actuelle]
        
        self.fields['matiere'].queryset = queryset
        self.fields['matiere'].label_from_instance = lambda obj: obj.nom
        self.fields['matiere'].empty_label = "-- Sélectionner une matière --"
    
    def clean_password2(self):
        cd = self.cleaned_data
        if 'password1' in cd and 'password2' in cd:
            if cd['password1'] != cd['password2']:
                raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return cd.get('password2')

    def clean_role(self):
        role = self.cleaned_data.get('role')
        from .models import RoleQuota
        if role and not RoleQuota.can_create_user(role):
            limit = RoleQuota.get_limit(role)
            current = RoleQuota.get_current_count(role)
            role_display = dict(Utilisateur.Role.choices).get(role, role)
            raise forms.ValidationError(f'Limite atteinte pour le rôle "{role_display}". Maximum: {limit}, Actuel: {current}')
        return role
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if 'password1' in self.cleaned_data:
            user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'adresse', 'matiere', 'is_active', 'est_approuve']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'role': forms.Select(attrs={'class': 'form-select', 'id': 'id_role'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'matiere': forms.Select(attrs={'class': 'form-select', 'id': 'id_matiere'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_approuve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Afficher uniquement le nom de la matière (sans coefficient)
        from django.db.models import Min
        from enseignement.models import Matiere
        ids_uniques = Matiere.objects.values('nom').annotate(id_min=Min('id')).values_list('id_min', flat=True)
        queryset = Matiere.objects.filter(id__in=ids_uniques).order_by('nom')
        
        # Si l'utilisateur a déjà une matière assignée qui n'est pas dans le queryset filtré,
        # on l'ajoute pour éviter les problèmes d'affichage
        if self.instance and self.instance.pk and self.instance.matiere_id:
            if not queryset.filter(id=self.instance.matiere_id).exists():
                matiere_actuelle = Matiere.objects.filter(id=self.instance.matiere_id).first()
                if matiere_actuelle:
                    queryset = list(queryset) + [matiere_actuelle]
        
        self.fields['matiere'].queryset = queryset
        self.fields['matiere'].label_from_instance = lambda obj: obj.nom
        self.fields['matiere'].empty_label = "-- Sélectionner une matière --"


class PermissionPersonnaliseeForm(forms.ModelForm):
    class Meta:
        model = PermissionPersonnalisee
        fields = ['utilisateur', 'module', 'actions', 'niveau', 'est_actif', 'est_temporaire', 'date_debut', 'date_fin']
        widgets = {
            'utilisateur': forms.Select(attrs={'class': 'form-select'}),
            'module': forms.Select(attrs={'class': 'form-select'}),
            'actions': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_temporaire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
