from django import forms
from .models import Bulletin


class BulletinForm(forms.ModelForm):
    class Meta:
        model = Bulletin
        fields = ['eleve', 'inscription', 'periode', 'appreciation']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'inscription': forms.Select(attrs={'class': 'form-select'}),
            'periode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Trimestre 1, Semestre 1...'}),
            'appreciation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Appréciation générale sur l\'élève'}),
        }
