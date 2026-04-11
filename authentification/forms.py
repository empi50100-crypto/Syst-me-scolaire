from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm as DjangoUserCreationForm
from .models import User


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
        choices=[('', 'Sélectionner votre service')] + list(User.Role.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'role')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError('Veuillez sélectionner votre service/fonction.')
        
        from .models import RoleQuota
        if not RoleQuota.can_create_user(role):
            limit = RoleQuota.get_limit(role)
            current = RoleQuota.get_current_count(role)
            role_display = dict(User.Role.choices).get(role, role)
            raise forms.ValidationError(f'Limite atteinte pour le rôle "{role_display}". Maximum: {limit}, Actuel: {current}')
        
        return role
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_approved = False
        user.is_active = True
        if commit:
            user.save()
        return user


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}))
    password2 = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'adresse', 'salaire_base', 'date_embauche', 'matiere', 'is_active', 'is_approved']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'salaire_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salaire en FCFA', 'min': '0'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from academics.models import Matiere
        self.fields['matiere'].queryset = Matiere.objects.all().order_by('nom')
        self.fields['matiere'].required = False
        self.fields['matiere'].label = 'Matière (pour enseignements)'
        
        role = self.data.get('role') or (self.instance.role if self.instance else None)
        if role != 'professeur':
            self.fields['matiere'].widget.attrs['disabled'] = True
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return cd['password2']

    def clean_role(self):
        role = self.cleaned_data.get('role')
        from .models import RoleQuota
        if role and not RoleQuota.can_create_user(role):
            limit = RoleQuota.get_limit(role)
            current = RoleQuota.get_current_count(role)
            role_display = dict(User.Role.choices).get(role, role)
            raise forms.ValidationError(f'Limite atteinte pour le rôle "{role_display}". Maximum: {limit}, Actuel: {current}')
        return role
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'adresse', 'salaire_base', 'date_embauche', 'matiere', 'is_active', 'is_approved']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +225 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'salaire_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salaire en FCFA', 'min': '0'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from academics.models import Matiere
        self.fields['matiere'].queryset = Matiere.objects.all().order_by('nom')
        self.fields['matiere'].required = False
        self.fields['matiere'].label = 'Matière (pour enseignements)'
