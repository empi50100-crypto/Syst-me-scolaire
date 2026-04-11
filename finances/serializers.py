from rest_framework import serializers
from finances.models import (
    FraisScolaire, Paiement, OperationCaisse,
    ChargeFixe, ChargeOperationnelle, Facture, BourseRemise
)
from core.models import AnneeScolaire
from ressources_humaines.models import MembrePersonnel, Salaire


class AnneeScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnneeScolaire
        fields = ['id', 'libelle', 'date_debut', 'date_fin', 'est_active']


class FraisScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraisScolaire
        fields = ['id', 'type_frais', 'montant', 'annee_scolaire', 'classe', 'description']


class PaiementSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = Paiement
        fields = ['id', 'eleve', 'eleve_nom', 'frais', 'montant', 'date_paiement', 'mode_paiement', 'reference']


class OperationCaisseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationCaisse
        fields = ['id', 'type_operation', 'montant', 'categorie', 'date_operation', 'personnel']


class SalaireSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source='employe.utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = Salaire
        fields = ['id', 'employe', 'employe_nom', 'mois', 'annee', 'salaire_brut', 'salaire_net', 'est_paye', 'date_versement']


class ChargeFixeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeFixe
        fields = ['id', 'type_charge', 'nom', 'montant', 'periodicite', 'est_active']


class ChargeOperationnelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeOperationnelle
        fields = ['id', 'type_charge', 'description', 'montant', 'date_charge', 'est_payee']


class MembrePersonnelSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = MembrePersonnel
        fields = ['id', 'utilisateur', 'utilisateur_nom', 'fonction', 'poste', 'telephone', 'date_embauche', 'est_actif']


class FactureSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = Facture
        fields = ['id', 'eleve', 'eleve_nom', 'numero_facture', 'montant_total', 'statut']


class BourseRemiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BourseRemise
        fields = ['id', 'nom', 'pourcentage', 'est_active']
