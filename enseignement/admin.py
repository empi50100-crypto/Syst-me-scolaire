from django.contrib import admin
from .models import (
    Classe, Matiere, ProfilProfesseur, Attribution, Evaluation, FicheNote,
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


@admin.register(ProfilProfesseur)
class ProfilProfesseurAdmin(admin.ModelAdmin):
    list_display = ['user', 'statut']
    list_filter = ['statut']


@admin.register(ContrainteHoraire)
class ContrainteHoraireAdmin(admin.ModelAdmin):
    list_display = ['professeur', 'jour', 'heure_debut', 'heure_fin', 'type_contrainte']
    list_filter = ['type_contrainte']


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau', 'serie', 'domaine', 'annee_scolaire', 'capacite']
    list_filter = ['niveau', 'annee_scolaire']


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):
    list_display = ['professeur', 'classe', 'matiere', 'annee_scolaire']
    list_filter = ['annee_scolaire', 'classe']


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ['nom', 'classe', 'matiere', 'date_examen', 'duree_minutes']
    list_filter = ['annee_scolaire', 'est_publie']
    search_fields = ['nom', 'classe__nom', 'matiere__nom']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'matiere', 'date_eval', 'note']
    list_filter = ['date_eval', 'matiere']
    search_fields = ['eleve__nom', 'eleve__prenom']


@admin.register(FicheNote)
class FicheNoteAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'classe', 'periode', 'moyenne', 'rang']
