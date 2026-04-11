from rest_framework import serializers
from finances.models import (
    AnneeScolaire, FraisScolaire, Paiement, EcoleCompte, Salaire,
    ChargeFixe, ChargeOperationnelle, Personnel, Facture, BourseRemise
)


class AnneeScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnneeScolaire
        fields = ['id', 'libelle', 'date_debut', 'date_fin', 'est_active', 'type_cycle_actif']


class FraisScolaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraisScolaire
        fields = ['id', 'type_frais', 'montant', 'annee_scolaire', 'classe', 'tranche', 'description']


class PaiementSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = Paiement
        fields = ['id', 'eleve', 'eleve_nom', 'frais', 'montant', 'date_paiement', 'mode_paiement', 'reference']


class EcoleCompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoleCompte
        fields = ['id', 'type_operation', 'montant', 'description', 'date_operation', 'personnel']


class SalaireSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source='employe.utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = Salaire
        fields = ['id', 'employe', 'employe_nom', 'mois', 'annee', 'salaire_brut', 'salaire_net', 'est_paye', 'date_versement']


class ChargeFixeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeFixe
        fields = ['id', 'type_charge', 'description', 'montant', 'periode', 'date_debut', 'est_active']


class ChargeOperationnelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeOperationnelle
        fields = ['id', 'type_charge', 'description', 'montant', 'date_depense', 'categorie']


class PersonnelSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = Personnel
        fields = ['id', 'nom', 'prenom', 'utilisateur_nom', 'fonction', 'telephone', 'salaire_mensuel', 'est_actif']


class FactureSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = Facture
        fields = ['id', 'eleve', 'eleve_nom', 'numero_facture', 'montant_total', 'montant_paye', 'statut', 'date_echeance']


class BourseRemiseSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    
    class Meta:
        model = BourseRemise
        fields = ['id', 'eleve', 'eleve_nom', 'type', 'montant', 'annee_scolaire', 'motif', 'est_appliquee']