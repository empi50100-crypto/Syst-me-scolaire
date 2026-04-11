from rest_framework import serializers
from scolarite.models import Eleve, ParentTuteur, EleveInscription, SanctionRecompense, DocumentEleve


class EleveSerializer(serializers.ModelSerializer):
    nom_complet = serializers.SerializerMethodField()
    
    class Meta:
        model = Eleve
        fields = ['id', 'matricule', 'nom', 'prenom', 'nom_complet', 'sexe', 'date_naissance', 
                  'lieu_naissance', 'statut', 'photo', 'niveau']
    
    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"


class ParentTuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTuteur
        fields = ['id', 'eleve', 'nom', 'prenom', 'lien_parente', 'telephone', 'email', 'adresse', 'profession']


class EleveInscriptionSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = EleveInscription
        fields = ['id', 'eleve', 'eleve_nom', 'classe', 'classe_nom', 'annee_scolaire', 'date_inscription']


class SanctionRecompenseSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = SanctionRecompense
        fields = ['id', 'eleve', 'eleve_nom', 'type', 'type_detail', 'description', 'date_incident', 'points']


class DocumentEleveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentEleve
        fields = ['id', 'eleve', 'type_document', 'fichier', 'date_upload']
