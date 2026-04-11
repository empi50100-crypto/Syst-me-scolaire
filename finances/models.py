from django.db import models
from decimal import Decimal


class CycleConfig(models.Model):
    class TypeCycle(models.TextChoices):
        TRIMESTRIEL = 'trimestriel', 'Trimestriel'
        SEMESTRIEL = 'semestriel', 'Semestriel'
    
    annee_scolaire = models.ForeignKey('AnneeScolaire', on_delete=models.CASCADE, related_name='cycles')
    type_cycle = models.CharField(max_length=20, choices=TypeCycle.choices)
    numero = models.PositiveIntegerField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    pourcentage = models.PositiveIntegerField(default=100, help_text="Pourcentage du montant total à payer")
    
    class Meta:
        verbose_name = 'Configuration du cycle'
        verbose_name_plural = 'Configurations des cycles'
        unique_together = ['annee_scolaire', 'type_cycle', 'numero']
        ordering = ['annee_scolaire', 'type_cycle', 'numero']
    
    def __str__(self):
        return f"{self.annee_scolaire.libelle} - {self.get_type_cycle_display()} {self.numero}"
    
    @property
    def libelle(self):
        prefix = "T" if self.type_cycle == self.TypeCycle.TRIMESTRIEL else "S"
        return f"{prefix}{self.numero}"


class AnneeScolaire(models.Model):
    class TypeCycle(models.TextChoices):
        TRIMESTRIEL = 'trimestriel', 'Trimestriel'
        SEMESTRIEL = 'semestriel', 'Semestriel'
    
    libelle = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_active = models.BooleanField(default=False)
    type_cycle_actif = models.CharField(max_length=20, choices=TypeCycle.choices, null=True, blank=True, help_text="Type de cycle actif pour cette année scolaire")
    
    class Meta:
        verbose_name = 'Année scolaire'
        verbose_name_plural = 'Années scolaires'
        ordering = ['-date_debut']
    
    def __str__(self):
        return self.libelle


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
    
    class NiveauClasse(models.TextChoices):
        CI = 'CI', 'Cours Initial'
        CP = 'CP', 'Cours Préparatoire'
        CE1 = 'CE1', 'Cours Élémentaire 1'
        CE2 = 'CE2', 'Cours Élémentaire 2'
        CM1 = 'CM1', 'Cours Moyen 1'
        CM2 = 'CM2', 'Cours Moyen 2'
        SIXIEME = '6e', 'Sixième'
        CINQUIEME = '5e', 'Cinquième'
        QUATRIEME = '4e', 'Quatrième'
        TROISIEME = '3e', 'Troisième'
        SECONDE = '2nde', 'Seconde'
        PREMIERE = '1re', 'Première'
        TERMINALE = 'Tle', 'Terminale'
    
    type_frais = models.CharField(max_length=20, choices=TypeFrais.choices)
    mode_application = models.CharField(max_length=20, choices=ModeApplication.choices, default=ModeApplication.DETAILLE)
    classe = models.ForeignKey('academics.Classe', on_delete=models.CASCADE, related_name='frais', null=True, blank=True, help_text="Pour mode 'Classes spécifiques'")
    niveau = models.CharField(max_length=10, choices=NiveauClasse.choices, null=True, blank=True, help_text="Pour mode 'Par niveau/filière'")
    filiere = models.CharField(max_length=50, blank=True, help_text="Filière spécifique (ex: A1, C, D). Laisser vide pour toutes les filières du niveau.")
    annee_scolaire = models.ForeignKey('AnneeScolaire', on_delete=models.CASCADE, related_name='frais', null=True, blank=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Frais scolaire'
        verbose_name_plural = 'Frais scolaires'
    
    def __str__(self):
        if self.mode_application == self.ModeApplication.GENERAL:
            return f"TOUTES - {self.get_type_frais_display()} - {self.montant} Fcfa"
        elif self.mode_application == self.ModeApplication.NIVEAU:
            filiere_txt = f" {self.filiere}" if self.filiere else ""
            return f"{self.get_niveau_display()}{filiere_txt} - {self.get_type_frais_display()} - {self.montant} Fcfa"
        return f"{self.classe.nom} - {self.get_type_frais_display()} - {self.montant} Fcfa"
    
    def get_classes_concernees(self):
        from academics.models import Classe
        if self.mode_application == self.ModeApplication.GENERAL:
            return Classe.objects.filter(annee_scolaire=self.annee_scolaire)
        elif self.mode_application == self.ModeApplication.NIVEAU:
            qs = Classe.objects.filter(annee_scolaire=self.annee_scolaire, niveau=self.niveau)
            if self.filiere:
                qs = qs.filter(filiere=self.filiere)
            return qs
        elif self.classe:
            return Classe.objects.filter(id=self.classe_id)
        return Classe.objects.none()
    
    def save(self, *args, **kwargs):
        if self.mode_application == self.ModeApplication.GENERAL:
            self.niveau = None
            self.filiere = ''
            self.classe = None
        elif self.mode_application == self.ModeApplication.NIVEAU:
            self.classe = None
        elif self.mode_application == self.ModeApplication.DETAILLE:
            self.niveau = None
            self.filiere = ''
        super().save(*args, **kwargs)


class Paiement(models.Model):
    class ModePaiement(models.TextChoices):
        ESPECE = 'espece', 'Espèces'
        VIREMENT = 'virement', 'Virement bancaire'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        CHEQUE = 'cheque', 'Chèque'
    
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='paiements')
    frais = models.ForeignKey(FraisScolaire, on_delete=models.CASCADE, related_name='paiements')
    date_paiement = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=ModePaiement.choices)
    reference = models.CharField(max_length=50, blank=True)
    personnel = models.ForeignKey('authentification.User', on_delete=models.SET_NULL, null=True)
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"{self.eleve} - {self.montant} ({self.date_paiement})"


class EcoleCompte(models.Model):
    date_operation = models.DateField()
    type_operation = models.CharField(max_length=20, choices=[('encaissement', 'Encaissement'), ('decaissement', 'Décaissement')])
    categorie = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    beneficiaire = models.CharField(max_length=200, blank=True)
    motif = models.TextField()
    personnel = models.ForeignKey('authentification.User', on_delete=models.SET_NULL, null=True)
    
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
    
    class Periodicite(models.TextChoices):
        MENSUELLE = 'mensuelle', 'Mensuelle'
        TRIMESTRIELLE = 'trimestrielle', 'Trimestrielle'
        SEMESTRIELLE = 'semestrielle', 'Semestrielle'
        ANNUELLE = 'annuelle', 'Annuelle'
        PONCTUELLE = 'ponctuelle', 'Ponctuelle'
    
    nom = models.CharField(max_length=200)
    type_charge = models.CharField(max_length=20, choices=TypeCharge.choices)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    periodicite = models.CharField(max_length=20, choices=Periodicite.choices, default=Periodicite.MENSUELLE)
    beneficiaire = models.CharField(max_length=200, blank=True, help_text="Propriétaire, société, etc.")
    description = models.TextField(blank=True)
    est_active = models.BooleanField(default=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Charge fixe'
        verbose_name_plural = 'Charges fixes'
        ordering = ['type_charge', 'nom']
    
    def __str__(self):
        return f"{self.nom} - {self.montant} FCFA ({self.get_periodicite_display()})"


class ChargeOperationnelle(models.Model):
    date_charge = models.DateField()
    type_charge = models.CharField(max_length=20, choices=ChargeFixe.TypeCharge.choices)
    description = models.CharField(max_length=300)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    fournisseur = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text="Numéro de facture, reçu, etc.")
    personnel = models.ForeignKey('authentification.User', on_delete=models.SET_NULL, null=True)
    est_payee = models.BooleanField(default=True)
    date_paiement = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Charge opérationnelle'
        verbose_name_plural = 'Charges opérationnelles'
        ordering = ['-date_charge']
    
    def __str__(self):
        return f"{self.date_charge} - {self.description} - {self.montant}"


class Personnel(models.Model):
    class Fonction(models.TextChoices):
        DIRECTION = 'direction', 'Direction'
        SECRETARIAT = 'secretaire', 'Secrétariat'
        COMPTABILITE = 'comptable', 'Comptabilité'
        ENSEIGNEMENT = 'professeur', 'Enseignant'
        SURVEILLANCE = 'surveillance', 'Surveillance'
        AGENT_SECURITE = 'agent_securite', 'Agent de Sécurité'
        CHAUFFEUR = 'chauffeur', 'Chauffeur'
        RESPONSABLE_STOCK = 'responsable_stock', 'Responsable Stock'
        MENAGE = 'menage', 'Agent d\'entretien/Ménage'
        MEDECIN = 'medecin', 'Médecin/Infirmier'
        AUTRE = 'autre', 'Autre'
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    fonction = models.CharField(max_length=25, choices=Fonction.choices)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    salaire_mensuel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire mensuel (FCFA)")
    date_embauche = models.DateField(null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    compte_utilisateur = models.OneToOneField('authentification.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='dossier_personnel')
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Personnel'
        verbose_name_plural = 'Personnel'
        ordering = ['fonction', 'nom']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.get_fonction_display()}"
    
    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"


class Salaire(models.Model):
    class StatutSalaire(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        PAYE = 'paye', 'Payé'
        EN_RETARD = 'en_retard', 'En retard'
    
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='salaires')
    mois = models.PositiveIntegerField(choices=[(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)])
    annee = models.PositiveIntegerField()
    salaire_brut = models.DecimalField(max_digits=10, decimal_places=2)
    retenues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2)
    date_versement = models.DateField(null=True, blank=True)
    est_paye = models.BooleanField(default=False, verbose_name="Payé")
    
    class Meta:
        verbose_name = 'Salaire du personnel'
        verbose_name_plural = 'Salaires du personnel'
        unique_together = ['personnel', 'mois', 'annee']
    
    def __str__(self):
        return f"{self.personnel} - {self.get_mois_display()} {self.annee}"
    
    def save(self, *args, **kwargs):
        self.salaire_net = self.salaire_brut - self.retenues
        super().save(*args, **kwargs)


class Rappel(models.Model):
    class StatutRappel(models.TextChoices):
        ENVOYE = 'envoye', 'Envoyé'
        ACQUITTE = 'acquitte', 'Acquitté'
        ANNULE = 'annule', 'Annulé'
    
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='rappels')
    type_rappel = models.CharField(max_length=50)
    date_emission = models.DateField(auto_now_add=True)
    date_echeance = models.DateField()
    montant_due = models.DecimalField(max_digits=10, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=StatutRappel.choices, default=StatutRappel.ENVOYE)
    date_acquittement = models.DateField(null=True, blank=True)
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Rappel'
        verbose_name_plural = 'Rappels'
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Rappel {self.eleve} - {self.date_echeance}"


class Facture(models.Model):
    class StatutFacture(models.TextChoices):
        PAYEE = 'payee', 'Payée'
        PARTIELLEMENT_PAYEE = 'partiellement_payee', 'Partiellement payée'
        EN_ATTENTE = 'en_attente', 'En attente'
        ANNULEE = 'annulee', 'Annulée'
    
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='factures')
    inscription = models.ForeignKey('eleves.Inscription', on_delete=models.CASCADE, related_name='factures', null=True, blank=True)
    numero_facture = models.CharField(max_length=50, unique=True)
    date_facture = models.DateField(auto_now_add=True)
    date_echeance = models.DateField()
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=StatutFacture.choices, default=StatutFacture.EN_ATTENTE)
    personnel = models.ForeignKey('authentification.User', on_delete=models.SET_NULL, null=True)
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_facture']
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.eleve}"
    
    def save(self, *args, **kwargs):
        if not self.numero_facture:
            import datetime
            self.numero_facture = f"FACT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    @property
    def montant_restant(self):
        return self.montant_total - self.montant_paye
    
    @property
    def est_soldee(self):
        return self.montant_restant <= 0


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    frais = models.ForeignKey(FraisScolaire, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Remise en pourcentage")
    
    class Meta:
        verbose_name = 'Ligne de facture'
        verbose_name_plural = 'Lignes de facture'
    
    def __str__(self):
        return f"{self.description} - {self.prix_unitaire}"
    
    @property
    def montant_ligne(self):
        return (self.prix_unitaire * self.quantite) * (1 - self.remise / 100)


class BourseRemise(models.Model):
    class Type(models.TextChoices):
        BOURSE = 'bourse', 'Bourse'
        REMISE = 'remise', 'Remise'
    
    nom = models.CharField(max_length=100)
    type_remise = models.CharField(max_length=20, choices=Type.choices)
    pourcentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Pourcentage de réduction")
    description = models.TextField(blank=True)
    est_active = models.BooleanField(default=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Bourse/Remise'
        verbose_name_plural = 'Bourses/Remises'
        ordering = ['-est_active', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.pourcentage}%)"


class EleveBourse(models.Model):
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='bourses')
    bourse = models.ForeignKey(BourseRemise, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey('AnneeScolaire', on_delete=models.CASCADE)
    pourcentage_accorde = models.DecimalField(max_digits=5, decimal_places=2)
    justification = models.TextField(blank=True)
    date_attribution = models.DateField(auto_now_add=True)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Élève boursier'
        verbose_name_plural = 'Élèves boursiers'
        unique_together = ['eleve', 'annee_scolaire']
    
    def __str__(self):
        return f"{self.eleve} - {self.bourse.nom} ({self.pourcentage_accorde}%)"


class CategorieDepense(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Catégorie de dépense'
        verbose_name_plural = 'Catégories de dépenses'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class RapportFinancier(models.Model):
    class TypeRapport(models.TextChoices):
        MENSUEL = 'mensuel', 'Mensuel'
        TRIMESTRIEL = 'trimestriel', 'Trimestriel'
        SEMESTRIEL = 'semestriel', 'Semestriel'
        ANNUEL = 'annuel', 'Annuel'
    
    type_rapport = models.CharField(max_length=20, choices=TypeRapport.choices)
    annee_scolaire = models.ForeignKey('AnneeScolaire', on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    total_recettes = models.DecimalField(max_digits=15, decimal_places=2)
    total_depenses = models.DecimalField(max_digits=15, decimal_places=2)
    total_salaires = models.DecimalField(max_digits=15, decimal_places=2)
    solde = models.DecimalField(max_digits=15, decimal_places=2)
    details_recettes = models.JSONField(default=dict, blank=True)
    details_depenses = models.JSONField(default=dict, blank=True)
    date_generation = models.DateField(auto_now_add=True)
    genere_par = models.ForeignKey('authentification.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Rapport financier'
        verbose_name_plural = 'Rapports financiers'
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"Rapport {self.get_type_rapport_display()} - {self.annee_scolaire}"
