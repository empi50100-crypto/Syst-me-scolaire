from rest_framework import serializers
from eleves.models import Eleve, ParentTuteur, Inscription, DisciplineEleve, DocumentEleve


class EleveSerializer(serializers.ModelSerializer):
    nom_complet = serializers.SerializerMethodField()
    classe_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Eleve
        fields = ['id', 'matricule', 'nom', 'prenom', 'nom_complet', 'sexe', 'date_naissance', 
                  'lieu_naissance', 'classe', 'classe_nom', 'statut', 'photo']
    
    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    
    def get_classe_nom(self, obj):
        return obj.classe.nom if obj.classe else None


class ParentTuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTuteur
        fields = ['id', 'eleve', 'nom', 'prenom', 'relation', 'telephone', 'email', 'adresse', 'profession']


class InscriptionSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    
    class Meta:
        model = Inscription
        fields = ['id', 'eleve', 'eleve_nom', 'classe', 'classe_nom', 'annee_scolaire', 'date_inscription', 'statut']


class DisciplineEleveSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = DisciplineEleve
        fields = ['id', 'eleve', 'eleve_nom', 'type_incident', 'description', 'date_incident', 'gravite', 'sanction']


class DocumentEleveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentEleve
        fields = ['id', 'eleve', 'type_document', 'fichier', 'date_upload']