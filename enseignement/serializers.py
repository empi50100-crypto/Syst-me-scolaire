from rest_framework import serializers
from .models import Classe, Matiere, Attribution, Evaluation, Salle, ProfilProfesseur, Examen, FicheNote


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau', 'serie', 'domaine', 'subdivision', 'annee_scolaire', 'capacite']


class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ['id', 'nom']


class AttributionSerializer(serializers.ModelSerializer):
    professeur_nom = serializers.CharField(source='professeur.user.get_full_name', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = Attribution
        fields = ['id', 'classe', 'classe_nom', 'matiere', 'matiere_nom', 'professeur', 'professeur_nom']


class EvaluationSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = ['id', 'eleve', 'eleve_nom', 'matiere', 'matiere_nom', 'note', 'coefficient', 'date_eval']


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ['id', 'nom', 'type_salle', 'capacite', 'etage', 'equipements']


class ExamenSerializer(serializers.ModelSerializer):
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    
    class Meta:
        model = Examen
        fields = ['id', 'nom', 'classe', 'classe_nom', 'matiere', 'matiere_nom', 'date_examen', 'duree_minutes', 'note_sur']


class FicheNoteSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = FicheNote
        fields = ['id', 'eleve', 'eleve_nom', 'classe', 'periode', 'moyenne', 'rang']
