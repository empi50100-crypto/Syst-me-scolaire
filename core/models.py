from django.db import models


class AnneeScolaire(models.Model):
    class TypeCycle(models.TextChoices):
        TRIMESTRIEL = 'trimestriel', 'Trimestriel'
        SEMESTRIEL = 'semestriel', 'Semestriel'
    
    libelle = models.CharField(max_length=50, verbose_name="Libellé")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    est_active = models.BooleanField(default=False, verbose_name="Année active")
    type_cycle_actif = models.CharField(max_length=20, choices=TypeCycle.choices, null=True, blank=True, verbose_name="Type de cycle actif")
    
    class Meta:
        verbose_name = 'Année scolaire'
        verbose_name_plural = 'Années scolaires'
        ordering = ['-date_debut']
    
    def __str__(self):
        return self.libelle


class Cycle(models.Model):
    class TypeCycle(models.TextChoices):
        TRIMESTRIEL = 'trimestriel', 'Trimestriel'
        SEMESTRIEL = 'semestriel', 'Semestriel'
    
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='cycles', verbose_name="Année scolaire")
    type_cycle = models.CharField(max_length=20, choices=TypeCycle.choices, verbose_name="Type de cycle")
    numero = models.PositiveIntegerField(verbose_name="Numéro")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    pourcentage = models.PositiveIntegerField(default=100, help_text="Pourcentage du montant total à payer")
    
    class Meta:
        verbose_name = 'Cycle'
        verbose_name_plural = 'Cycles'
        unique_together = ['annee_scolaire', 'type_cycle', 'numero']
        ordering = ['annee_scolaire', 'type_cycle', 'numero']
    
    def __str__(self):
        prefix = "T" if self.type_cycle == self.TypeCycle.TRIMESTRIEL else "S"
        return f"{self.annee_scolaire.libelle} - {prefix}{self.numero}"
    
    @property
    def libelle(self):
        prefix = "T" if self.type_cycle == self.TypeCycle.TRIMESTRIEL else "S"
        return f"{prefix}{self.numero}"


class NiveauScolaire(models.Model):
    class Niveau(models.TextChoices):
        MATERNELLE_1 = 'maternelle_1', 'Maternelle 1'
        MATERNELLE_2 = 'maternelle_2', 'Maternelle 2'
        MATERNELLE_3 = 'maternelle_3', 'Maternelle 3'
        CP = 'cp', 'Cours Préparatoire'
        CE1 = 'ce1', 'Cours Élémentaire 1'
        CE2 = 'ce2', 'Cours Élémentaire 2'
        CM1 = 'cm1', 'Cours Moyen 1'
        CM2 = 'cm2', 'Cours Moyen 2'
        SIXIEME = '6e', 'Sixième'
        CINQUIEME = '5e', 'Cinquième'
        QUATRIEME = '4e', 'Quatrième'
        TROISIEME = '3e', 'Troisième'
        SECONDE = '2nde', 'Seconde'
        PREMIERE = '1re', 'Première'
        TERMINALE = 'tle', 'Terminale'
        LICENCE_1 = 'l1', 'Licence 1'
        LICENCE_2 = 'l2', 'Licence 2'
        LICENCE_3 = 'l3', 'Licence 3'
        MASTER_1 = 'm1', 'Master 1'
        MASTER_2 = 'm2', 'Master 2'
    
    niveau = models.CharField(max_length=20, choices=Niveau.choices, unique=True, verbose_name="Niveau")
    libelle = models.CharField(max_length=50, verbose_name="Libellé")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    class Meta:
        verbose_name = 'Niveau scolaire'
        verbose_name_plural = 'Niveaux scolaires'
        ordering = ['ordre']
    
    def __str__(self):
        return self.libelle


class PeriodeEvaluation(models.Model):
    class TypePeriode(models.TextChoices):
        TRIMESTRE = 'trimestre', 'Trimestre'
        SEMESTRE = 'semestre', 'Semestre'
    
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='periodes_evaluation', verbose_name="Année scolaire")
    type_periode = models.CharField(max_length=20, choices=TypePeriode.choices, verbose_name="Type de période")
    numero = models.PositiveIntegerField(verbose_name="Numéro")
    debut = models.DateField(verbose_name="Date de début")
    fin = models.DateField(verbose_name="Date de fin")
    
    class Meta:
        verbose_name = 'Période d\'évaluation'
        verbose_name_plural = 'Périodes d\'évaluation'
        unique_together = ['annee_scolaire', 'type_periode', 'numero']
        ordering = ['annee_scolaire', 'numero']
    
    def __str__(self):
        return f"{self.annee_scolaire.libelle} - {self.get_type_periode_display()} {self.numero}"


class ConfigurationEtablissement(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom de l'établissement")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    site_web = models.URLField(blank=True, verbose_name="Site web")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logo")
    directeur = models.CharField(max_length=100, blank=True, verbose_name="Directeur")
    
    class Meta:
        verbose_name = 'Configuration de l\'établissement'
        verbose_name_plural = 'Configurations de l\'établissement'
    
    def __str__(self):
        return self.nom