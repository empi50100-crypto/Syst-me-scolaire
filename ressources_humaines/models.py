from django.db import models
from django.conf import settings


class FichePoste(models.Model):
    class TypeContrat(models.TextChoices):
        CDI = 'cdi', 'Contrat à durée indéterminée'
        CDD = 'cdd', 'Contrat à durée déterminée'
        STAGE = 'stage', 'Stage'
        INTERIM = 'interim', 'Intérim'
    
    titre = models.CharField(max_length=150, verbose_name="Titre du poste")
    description = models.TextField(verbose_name="Description du poste")
    type_contrat = models.CharField(max_length=20, choices=TypeContrat.choices, verbose_name="Type de contrat")
    salaire_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salaire minimum")
    salaire_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salaire maximum")
    exigences = models.TextField(blank=True, verbose_name="Exigences du poste")
    est_active = models.BooleanField(default=True, verbose_name="Poste actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fiche de poste'
        verbose_name_plural = 'Fiches de postes'
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.titre


class TypeConge(models.Model):
    """Types de congés (annuel, maladie, exceptionnel, etc.)"""
    nom = models.CharField(max_length=100, verbose_name="Nom du type")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    jours_annuels = models.PositiveIntegerField(default=0, verbose_name="Jours alloués par an")
    est_paye = models.BooleanField(default=True, verbose_name="Est payé")
    est_deductible = models.BooleanField(default=False, verbose_name="Déductible des jours")
    couleur = models.CharField(max_length=7, default='#4472C4', verbose_name="Couleur")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = 'Type de congé'
        verbose_name_plural = 'Types de congés'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Conge(models.Model):
    """Demandes de congés"""
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        APPROUVE = 'approuve', 'Approuvé'
        REJETE = 'rejete', 'Rejeté'
        ANNULE = 'annule', 'Annulé'
    
    employe = models.ForeignKey('MembrePersonnel', on_delete=models.CASCADE, related_name='conges', verbose_name="Employé")
    type_conge = models.ForeignKey(TypeConge, on_delete=models.PROTECT, verbose_name="Type de congé")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    jours = models.PositiveIntegerField(verbose_name="Nombre de jours")
    motif = models.TextField(verbose_name="Motif")
    remplissant = models.ForeignKey('MembrePersonnel', on_delete=models.SET_NULL, null=True, blank=True, related_name='conges_remplacement', verbose_name="Remplaçant")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE, verbose_name="Statut")
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    traite_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='conges_traites', verbose_name="Traité par")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    
    class Meta:
        verbose_name = 'Congé'
        verbose_name_plural = 'Congés'
        ordering = ['-date_demande']
    
    def __str__(self):
        return f"{self.employe} - {self.type_conge.nom} ({self.date_debut} - {self.date_fin})"
    
    def save(self, *args, **kwargs):
        if not self.jours:
            self.jours = (self.date_fin - self.date_debut).days + 1
        super().save(*args, **kwargs)


class Absence(models.Model):
    """Absences non planifiées"""
    class TypeAbsence(models.TextChoices):
        MALADIE = 'maladie', 'Maladie'
        ACCIDENT = 'accident', 'Accident'
        FAMILLE = 'famille', 'Famille'
        AUTRE = 'autre', 'Autre'
    
    class StatutAbsence(models.TextChoices):
        NON_JUSTIFIEE = 'non_justifiee', 'Non justifiée'
        JUSTIFIEE = 'justifiee', 'Justifiée'
        EN_COURS = 'en_cours', 'En cours de traitement'
    
    employe = models.ForeignKey('MembrePersonnel', on_delete=models.CASCADE, related_name='absences', verbose_name="Employé")
    type_absence = models.CharField(max_length=20, choices=TypeAbsence.choices, verbose_name="Type")
    date_absence = models.DateField(verbose_name="Date")
    heures = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name="Heures d'absence")
    est_justifiee = models.BooleanField(default=False, verbose_name="Justifiée")
    motif = models.TextField(blank=True, verbose_name="Motif")
    document = models.FileField(upload_to='absences/', null=True, blank=True, verbose_name="Justificatif")
    statut = models.CharField(max_length=20, choices=StatutAbsence.choices, default=StatutAbsence.NON_JUSTIFIEE, verbose_name="Statut")
    
    class Meta:
        verbose_name = 'Absence'
        verbose_name_plural = 'Absences'
        ordering = ['-date_absence']
    
    def __str__(self):
        return f"{self.employe} - {self.date_absence} ({self.get_type_absence_display()})"


class SoldeConge(models.Model):
    """Solde de congés par employé et par année"""
    employe = models.ForeignKey('MembrePersonnel', on_delete=models.CASCADE, related_name='soldes_conges', verbose_name="Employé")
    annee = models.PositiveIntegerField(verbose_name="Année")
    type_conge = models.ForeignKey(TypeConge, on_delete=models.CASCADE, verbose_name="Type de congé")
    jours_pris = models.PositiveIntegerField(default=0, verbose_name="Jours pris")
    jours_restants = models.PositiveIntegerField(verbose_name="Jours restants")
    
    class Meta:
        verbose_name = 'Solde de congés'
        verbose_name_plural = 'Soldes de congés'
        unique_together = ['employe', 'annee', 'type_conge']
    
    def __str__(self):
        return f"{self.employe} - {self.type_conge.nom} - {self.annee}: {self.jours_restants} jours"


class ContratEmploye(models.Model):
    class StatutContrat(models.TextChoices):
        ACTIF = 'actif', 'Actif'
        EXPIRE = 'expire', 'Expiré'
        RESILIE = 'resilie', 'Résilié'
    
    employe = models.ForeignKey('MembrePersonnel', on_delete=models.CASCADE, related_name='contrats')
    poste = models.ForeignKey(FichePoste, on_delete=models.SET_NULL, null=True, blank=True, related_name='contrats')
    type_contrat = models.CharField(max_length=20, choices=FichePoste.TypeContrat.choices, verbose_name="Type de contrat")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    salaire_brut = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire brut mensuel")
    conditions = models.TextField(blank=True, verbose_name="Conditions particulières")
    statut = models.CharField(max_length=20, choices=StatutContrat.choices, default=StatutContrat.ACTIF, verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Contrat employé'
        verbose_name_plural = 'Contrats employés'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.employe} - {self.type_contrat}"


class MembrePersonnel(models.Model):
    class Fonction(models.TextChoices):
        DIRECTION = 'direction', 'Direction'
        SECRETARIAT = 'secretaire', 'Secrétaire'
        COMPTABILITE = 'comptable', 'Comptabilité'
        ENSEIGNEMENT = 'professeur', 'Enseignant'
        SURVEILLANCE = 'surveillance', 'Surveillance'
        AGENT_SECURITE = 'agent_securite', 'Agent de Sécurité'
        CHAUFFEUR = 'chauffeur', 'Chauffeur'
        RESPONSABLE_STOCK = 'responsable_stock', 'Responsable Stock'
        MENAGE = 'menage', 'Agent d\'entretien/Ménage'
        MEDECIN = 'medecin', 'Médecin/Infirmier'
        AUTRE = 'autre', 'Autre'
    
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_personnel',
        verbose_name="Utilisateur"
    )
    fonction = models.CharField(max_length=25, choices=Fonction.choices, verbose_name="Fonction")
    poste = models.ForeignKey(FichePoste, on_delete=models.SET_NULL, null=True, blank=True, related_name='membres', verbose_name="Poste")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    date_embauche = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    observations = models.TextField(blank=True, verbose_name="Observations")
    
    class Meta:
        verbose_name = 'Membre du personnel'
        verbose_name_plural = 'Membres du personnel'
        ordering = ['fonction', 'utilisateur__last_name']
    
    def __str__(self):
        return f"{self.utilisateur.get_full_name() or self.utilisateur.username} - {self.get_fonction_display()}"
    
    @property
    def nom_complet(self):
        return self.utilisateur.get_full_name() or self.utilisateur.username


class Salaire(models.Model):
    class StatutSalaire(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        PAYE = 'paye', 'Payé'
        EN_RETARD = 'en_retard', 'En retard'
    
    employe = models.ForeignKey(MembrePersonnel, on_delete=models.CASCADE, related_name='salaires', verbose_name="Employé")
    mois = models.PositiveIntegerField(choices=[(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)], verbose_name="Mois")
    annee = models.PositiveIntegerField(verbose_name="Année")
    salaire_brut = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire brut")
    retenue_cnps = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Retenue CNPS")
    retenue_irpp = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Retenue IRPP")
    autres_retenues = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Autres retenues")
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire net")
    date_versement = models.DateField(null=True, blank=True, verbose_name="Date de versement")
    est_paye = models.BooleanField(default=False, verbose_name="Payé")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = 'Salaire'
        verbose_name_plural = 'Salaires'
        unique_together = ['employe', 'mois', 'annee']
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"{self.employe} - {self.get_mois_display()} {self.annee}"
    
    def save(self, *args, **kwargs):
        self.salaire_net = self.salaire_brut - self.retenue_cnps - self.retenue_irpp - self.autres_retenues
        super().save(*args, **kwargs)


class FichePaie(models.Model):
    salaire = models.OneToOneField(Salaire, on_delete=models.CASCADE, related_name='fiche_paie', verbose_name="Salaire")
    periode = models.CharField(max_length=50, verbose_name="Période")
    date_generation = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='fiches_paie/', null=True, blank=True, verbose_name="Fichier PDF")
    
    class Meta:
        verbose_name = 'Fiche de paie'
        verbose_name_plural = 'Fiches de paie'
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"Fiche de paie - {self.salaire}"