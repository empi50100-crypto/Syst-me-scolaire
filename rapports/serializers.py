from rest_framework import serializers
from django.contrib.auth import get_user_model
from eleves.models import Eleve, Inscription
from academics.models import Classe, Matiere, Professeur, Enseignement, Evaluation
from finances.models import AnneeScolaire, FraisScolaire, Paiement, Salaire
from presences.models import Presence

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'is_active']
        read_only_fields = ['id']


class EleveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleve
        fields = ['id', 'matricule', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
                  'sexe', 'adresse', 'telephone_parent', 'email_parent', 'statut']
        read_only_fields = ['id', 'matricule']


class InscriptionSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = Inscription
        fields = ['id', 'eleve', 'eleve_nom', 'classe', 'classe_nom', 'annee_scolaire',
                  'date_inscription', 'moyenne_generale', 'mention', 'decision', 'rang']
        read_only_fields = ['id']


class ClasseSerializer(serializers.ModelSerializer):
    niveau_display = serializers.CharField(source='get_niveau_display', read_only=True)
    
    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau', 'niveau_display', 'filiere', 'annee_scolaire', 'capacite']
        read_only_fields = ['id']


class MatiereSerializer(serializers.ModelSerializer):
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = Matiere
        fields = ['id', 'nom', 'coefficient', 'classe', 'classe_nom']
        read_only_fields = ['id']


class ProfesseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professeur
        fields = ['id', 'nom', 'prenom', 'email', 'telephone', 'date_embauche', 'statut', 'salaire_base']
        read_only_fields = ['id']


class EnseignementSerializer(serializers.ModelSerializer):
    professeur_nom = serializers.CharField(source='professeur.nom_complet', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = Enseignement
        fields = ['id', 'professeur', 'professeur_nom', 'classe', 'classe_nom', 'matiere', 'matiere_nom']
        read_only_fields = ['id']


class EvaluationSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    type_eval_display = serializers.CharField(source='get_type_eval_display', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = ['id', 'eleve', 'eleve_nom', 'matiere', 'matiere_nom', 'type_eval',
                  'type_eval_display', 'date_eval', 'note', 'coefficient', 'observations']
        read_only_fields = ['id']


class AnneeScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnneeScolaire
        fields = ['id', 'libelle', 'date_debut', 'date_fin', 'est_active']
        read_only_fields = ['id']


class FraisScolaireSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_frais_display', read_only=True)
    
    class Meta:
        model = FraisScolaire
        fields = ['id', 'classe', 'annee_scolaire', 'type_frais', 'type_display', 'montant', 'echeance']
        read_only_fields = ['id']


class PaiementSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    frais_type = serializers.CharField(source='frais.get_type_frais_display', read_only=True)
    mode_display = serializers.CharField(source='get_mode_paiement_display', read_only=True)
    
    class Meta:
        model = Paiement
        fields = ['id', 'eleve', 'eleve_nom', 'frais', 'frais_type', 'date_paiement',
                  'montant', 'mode_paiement', 'mode_display', 'reference', 'observations']
        read_only_fields = ['id']


class PresenceSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Presence
        fields = ['id', 'eleve', 'eleve_nom', 'classe', 'date', 'statut', 'statut_display',
                  'motif_absence', 'justifie', 'observations']
        read_only_fields = ['id']


class SalaireSerializer(serializers.ModelSerializer):
    personnel_nom = serializers.CharField(source='personnel.get_full_name', read_only=True)
    mois_display = serializers.CharField(source='get_mois_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Salaire
        fields = ['id', 'personnel', 'personnel_nom', 'mois', 'mois_display', 'annee',
                  'salaire_brut', 'retenues', 'salaire_net', 'date_versement', 'statut', 'statut_display']
        read_only_fields = ['id']
