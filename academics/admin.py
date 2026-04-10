from django.contrib import admin
from .models import (
    Classe, Matiere, Professeur, Enseignement, Evaluation, FicheNote,
    Salle, CoefficientMatiere, Examen, Epreuve, ContrainteHoraire
)


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_salle', 'capacite', 'etage', 'est_disponible']
    list_filter = ['type_salle', 'est_disponible']


@admin.register(CoefficientMatiere)
class CoefficientMatiereAdmin(admin.ModelAdmin):
    list_display = ['classe', 'matiere', 'coefficient']
    list_filter = ['classe']


@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'statut', 'date_embauche']
    list_filter = ['statut', 'date_embauche']
    search_fields = ['nom', 'prenom', 'email']


@admin.register(ContrainteHoraire)
class ContrainteHoraireAdmin(admin.ModelAdmin):
    list_display = ['professeur', 'jour', 'heure_debut', 'heure_fin', 'type_contrainte', 'est_recurrent']
    list_filter = ['type_contrainte', 'est_recurrent']
    search_fields = ['professeur__nom', 'professeur__prenom']


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau', 'serie', 'domaine', 'annee_scolaire', 'capacite']
    list_filter = ['niveau', 'annee_scolaire']


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ['nom', 'coefficient']
    search_fields = ['nom']


@admin.register(Enseignement)
class EnseignementAdmin(admin.ModelAdmin):
    list_display = ['professeur', 'classe', 'matiere', 'annee_scolaire']
    list_filter = ['annee_scolaire', 'classe']


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_examen', 'classe', 'matiere', 'date_examen', 'duree_minutes']
    list_filter = ['type_examen', 'annee_scolaire', 'est_publie']
    search_fields = ['nom', 'classe__nom', 'matiere__nom']


class EpreuveInline(admin.TabularInline):
    model = Epreuve
    extra = 0
    readonly_fields = ['eleve', 'note', 'est_corrige']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'matiere', 'type_eval', 'date_eval', 'note']
    list_filter = ['type_eval', 'date_eval', 'matiere']
    search_fields = ['eleve__nom', 'eleve__prenom']


@admin.register(FicheNote)
class FicheNoteAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'matiere', 'cycle', 'moyenne', 'rang']
    list_filter = ['cycle']
    search_fields = ['eleve__nom', 'eleve__prenom']
