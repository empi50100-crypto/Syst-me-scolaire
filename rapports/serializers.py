from rest_framework import serializers
from django.contrib.auth import get_user_model
from scolarite.models import Eleve, EleveInscription
from enseignement.models import Classe, Matiere, ProfilProfesseur, Attribution, Evaluation
from finances.models import AnneeScolaire, FraisScolaire, Paiement
from ressources_humaines.models import Salaire
from presences.models import Presence

Utilisateur = get_user_model()


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'is_active']
        read_only_fields = ['id']


class EleveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleve
        fields = ['id', 'matricule', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
                  'sexe', 'adresse', 'telephone_parent', 'email_parent', 'statut']
        read_only_fields = ['id', 'matricule']


class EleveInscriptionSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = EleveInscription
        fields = ['id', 'eleve', 'eleve_nom', 'classe', 'classe_nom', 'annee_scolaire',
                  'date_inscription', 'moyenne_generale', 'mention', 'decision', 'rang']
        read_only_fields = ['id']


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau', 'serie', 'domaine', 'annee_scolaire', 'capacite']
        read_only_fields = ['id']


class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ['id', 'nom']
        read_only_fields = ['id']


class ProfilProfesseurSerializer(serializers.ModelSerializer):
    nom_complet = serializers.CharField(source='user.get_full_name', read_only=True)
    class Meta:
        model = ProfilProfesseur
        fields = ['id', 'user', 'nom_complet', 'statut']
        read_only_fields = ['id']


class AttributionSerializer(serializers.ModelSerializer):
    professeur_nom = serializers.CharField(source='professeur.user.get_full_name', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = Attribution
        fields = ['id', 'professeur', 'professeur_nom', 'classe', 'classe_nom', 'matiere', 'matiere_nom']
        read_only_fields = ['id']


class EvaluationSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = ['id', 'eleve', 'eleve_nom', 'matiere', 'matiere_nom', 'date_eval', 'note', 'coefficient']
        read_only_fields = ['id']


class AnneeScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnneeScolaire
        fields = ['id', 'libelle', 'date_debut', 'date_fin', 'est_active']
        read_only_fields = ['id']


class FraisScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraisScolaire
        fields = ['id', 'classe', 'annee_scolaire', 'type_frais', 'montant']
        read_only_fields = ['id']


class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = ['id', 'eleve', 'frais', 'date_paiement', 'montant', 'mode_paiement']
        read_only_fields = ['id']


class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['id', 'eleve', 'classe', 'date', 'statut', 'justifie']
        read_only_fields = ['id']


class SalaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salaire
        fields = ['id', 'employe', 'mois', 'annee', 'salaire_net', 'est_paye']
        read_only_fields = ['id']
