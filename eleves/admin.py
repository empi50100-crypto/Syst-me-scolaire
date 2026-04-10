from django.contrib import admin
from .models import Eleve, Inscription, ParentTuteur, DossierMedical, DocumentEleve, DisciplineEleve, ConduiteConfig, ConduiteEleve


class ParentTuteurInline(admin.TabularInline):
    model = ParentTuteur
    extra = 1


class DossierMedicalInline(admin.StackedInline):
    model = DossierMedical
    extra = 0


class DocumentEleveInline(admin.TabularInline):
    model = DocumentEleve
    extra = 0


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'nom', 'prenom', 'date_naissance', 'sexe', 'statut']
    list_filter = ['statut', 'sexe', 'date_inscription']
    search_fields = ['matricule', 'nom', 'prenom', 'email_parent']
    readonly_fields = ['matricule', 'date_inscription']
    inlines = [ParentTuteurInline, DossierMedicalInline, DocumentEleveInline]


@admin.register(ParentTuteur)
class ParentTuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'lien_parente', 'telephone', 'whatsapp', 'est_contact_principal']
    list_filter = ['lien_parente', 'est_contact_principal']
    search_fields = ['nom', 'prenom', 'telephone', 'whatsapp']


@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'groupe_sanguin', 'date_derniere_mise_a_jour']
    search_fields = ['eleve__nom', 'eleve__prenom']


@admin.register(DocumentEleve)
class DocumentEleveAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'type_document', 'description', 'date_upload']
    list_filter = ['type_document']
    search_fields = ['eleve__nom', 'eleve__prenom', 'description']


@admin.register(DisciplineEleve)
class DisciplineEleveAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'type', 'type_detail', 'date_incident', 'statut_traitement', 'points', 'est_signale']
    list_filter = ['type', 'statut_traitement', 'est_signale', 'type_detail']
    search_fields = ['eleve__nom', 'eleve__prenom', 'description']
    date_hierarchy = 'date_incident'


@admin.register(ConduiteConfig)
class ConduiteConfigAdmin(admin.ModelAdmin):
    list_display = ['annee_scolaire', 'niveau', 'note_base', 'cree_par']
    list_filter = ['annee_scolaire', 'niveau']
    search_fields = ['niveau']


@admin.register(ConduiteEleve)
class ConduiteEleveAdmin(admin.ModelAdmin):
    list_display = ['inscription', 'note_base', 'total_deductions', 'total_recompenses', 'note_finale']
    search_fields = ['inscription__eleve__nom', 'inscription__eleve__prenom']


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'classe', 'annee_scolaire', 'moyenne_generale', 'mention']
    list_filter = ['annee_scolaire', 'decision']
    search_fields = ['eleve__nom', 'eleve__prenom', 'eleve__matricule']
