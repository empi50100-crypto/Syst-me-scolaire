from django.db import models
from decimal import Decimal
from core.models import AnneeScolaire, Cycle
from ressources_humaines.models import MembrePersonnel


class FraisScolaire(models.Model):
    class TypeFrais(models.TextChoices):
        INSCRIPTION = 'inscription', 'Frais d\'inscription'
        SCOLARITE = 'scolarite', 'Frais de scolarité'
        BIBLIOTHEQUE = 'bibliotheque', 'Bibliothèque'
        ACTIVITES = 'activites', 'Activités'
        TRANSPORT = 'transport', 'Transport'
        CANTINE = 'cantine', 'Cantine'
        AUTRE = 'autre', 'Autre'
    
    class ModeApplication(models.TextChoices):
        GENERAL = 'general', 'Toutes les classes'
        NIVEAU = 'niveau', 'Par niveau/filière'
        DETAILLE = 'detaille', 'Classes spécifiques'
    
    type_frais = models.CharField(max_length=20, choices=TypeFrais.choices)
    mode_application = models.CharField(max_length=20, choices=ModeApplication.choices, default=ModeApplication.DETAILLE)
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='frais', null=True, blank=True)
    niveau = models.ForeignKey('core.NiveauScolaire', on_delete=models.SET_NULL, null=True, blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='frais')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Frais scolaire'
        verbose_name_plural = 'Frais scolaires'
    
    def __str__(self):
        return f"{self.get_type_frais_display()} - {self.montant} FCFA"


class Paiement(models.Model):
    class ModePaiement(models.TextChoices):
        ESPECE = 'espece', 'Espèces'
        VIREMENT = 'virement', 'Virement bancaire'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        CHEQUE = 'cheque', 'Chèque'
    
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='paiements')
    frais = models.ForeignKey(FraisScolaire, on_delete=models.CASCADE, related_name='paiements')
    date_paiement = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=ModePaiement.choices)
    reference = models.CharField(max_length=50, blank=True)
    encaisse_par = models.ForeignKey('authentification.Utilisateur', on_delete=models.SET_NULL, null=True)
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"{self.eleve} - {self.montant} ({self.date_paiement})"


class OperationCaisse(models.Model):
    date_operation = models.DateField()
    type_operation = models.CharField(max_length=20, choices=[('encaissement', 'Encaissement'), ('decaissement', 'Décaissement')])
    categorie = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    beneficiaire = models.CharField(max_length=200, blank=True)
    motif = models.TextField()
    personnel = models.ForeignKey('authentification.Utilisateur', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Opération de caisse'
        verbose_name_plural = 'Opérations de caisse'
        ordering = ['-date_operation']
    
    def __str__(self):
        return f"{self.date_operation} - {self.type_operation} - {self.montant}"


class ChargeFixe(models.Model):
    class TypeCharge(models.TextChoices):
        LOYER = 'loyer', 'Loyer'
        ELECTRICITE = 'electricite', 'Électricité'
        EAU = 'eau', 'Eau'
        INTERNET = 'internet', 'Internet'
        ASSURANCE = 'assurance', 'Assurance'
        IMPOTS = 'impots', 'Impôts et Taxes'
        MAINTENANCE = 'maintenance', 'Maintenance'
        FOURNITURES = 'fournitures', 'Fournitures'
        TRANSPORT = 'transport', 'Transport'
        AUTRE = 'autre', 'Autre'
    
    nom = models.CharField(max_length=200)
    type_charge = models.CharField(max_length=20, choices=TypeCharge.choices)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    periodicite = models.CharField(max_length=20, default='mensuelle')
    est_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Charge fixe'
        verbose_name_plural = 'Charges fixes'
    
    def __str__(self):
        return self.nom


class ChargeOperationnelle(models.Model):
    date_charge = models.DateField()
    type_charge = models.CharField(max_length=20, choices=ChargeFixe.TypeCharge.choices)
    description = models.CharField(max_length=300)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    fournisseur = models.CharField(max_length=200, blank=True)
    est_payee = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Charge opérationnelle'
        verbose_name_plural = 'Charges opérationnelles'
    
    def __str__(self):
        return f"{self.date_charge} - {self.description}"


class RappelPaiement(models.Model):
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='rappels')
    date_echeance = models.DateField()
    montant_due = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, default='envoye')
    
    class Meta:
        verbose_name = 'Rappel de paiement'
        verbose_name_plural = 'Rappels de paiements'
    
    def __str__(self):
        return f"Rappel {self.eleve}"


class Facture(models.Model):
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='factures')
    numero_facture = models.CharField(max_length=50, unique=True)
    date_facture = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    statut = models.CharField(max_length=20, default='en_attente')
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
    
    def __str__(self):
        return self.numero_facture


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    description = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Ligne de facture'
        verbose_name_plural = 'Lignes de facture'


class BourseRemise(models.Model):
    nom = models.CharField(max_length=100)
    pourcentage = models.DecimalField(max_digits=5, decimal_places=2)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Bourse/Remise'
        verbose_name_plural = 'Bourses/Remises'
    
    def __str__(self):
        return self.nom


class EleveBourse(models.Model):
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='bourses')
    bourse = models.ForeignKey(BourseRemise, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Élève boursier'
        verbose_name_plural = 'Élèves boursiers'
        unique_together = ['eleve', 'annee_scolaire']


class CategorieDepense(models.Model):
    nom = models.CharField(max_length=100)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Catégorie de dépense'
        verbose_name_plural = 'Catégories de dépenses'
    
    def __str__(self):
        return self.nom


class RapportFinancier(models.Model):
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    total_recettes = models.DecimalField(max_digits=15, decimal_places=2)
    total_depenses = models.DecimalField(max_digits=15, decimal_places=2)
    solde = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        verbose_name = 'Rapport financier'
        verbose_name_plural = 'Rapports financiers'
