from django.db import models
from django.conf import settings
from core.models import AnneeScolaire, Cycle, NiveauScolaire, PeriodeEvaluation


class Salle(models.Model):
    class TypeSalle(models.TextChoices):
        CLASSE = 'classe', 'Salle de classe'
        LABORATOIRE = 'laboratoire', 'Laboratoire'
        INFORMATIQUE = 'informatique', 'Salle informatique'
        SPORT = 'sport', 'Salle de sport'
        BIBLIOTHEQUE = 'bibliotheque', 'Bibliothèque'
        AUTRE = 'autre', 'Autre'
    
    nom = models.CharField(max_length=100)
    type_salle = models.CharField(max_length=20, choices=TypeSalle.choices, default=TypeSalle.CLASSE)
    capacite = models.PositiveIntegerField(default=40)
    etage = models.CharField(max_length=20, blank=True, help_text="Ex: RDC, 1er étage")
    equipements = models.TextField(blank=True, help_text="Vidéoprojecteur, tableau interactif, etc.")
    est_disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Salle'
        verbose_name_plural = 'Salles'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_salle_display()})"


class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class ProfilProfesseur(models.Model):
    user = models.OneToOneField('authentification.Utilisateur', on_delete=models.CASCADE, related_name='profil_professeur')
    statut = models.CharField(max_length=20, default='actif')
    specialite = models.ForeignKey(Matiere, on_delete=models.SET_NULL, null=True, blank=True, related_name='specialistes')
    
    class Meta:
        verbose_name = 'Profil Professeur'
        verbose_name_plural = 'Profils Professeurs'
    
    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"


class Classe(models.Model):
    nom = models.CharField(max_length=50, verbose_name="Nom de la classe")
    niveau = models.ForeignKey(NiveauScolaire, on_delete=models.CASCADE, related_name='classes', verbose_name="Niveau")
    serie = models.CharField(max_length=10, blank=True, verbose_name="Série (Lycée)")
    domaine = models.CharField(max_length=50, blank=True, verbose_name="Domaine (Université)")
    subdivision = models.CharField(max_length=50, blank=True, verbose_name="Subdivision (ex: 1, 2, A, B...)")
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='classes')
    capacite = models.PositiveIntegerField(default=40)
    professeur_principal = models.ForeignKey(ProfilProfesseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes_principales')
    note_conduite_base = models.PositiveIntegerField(default=20)
    matieres = models.ManyToManyField(Matiere, through='CoefficientMatiere', related_name='classes')
    
    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        unique_together = ['nom', 'serie', 'domaine', 'subdivision', 'annee_scolaire']
    
    def __str__(self):
        return f"{self.nom} {self.subdivision} ({self.annee_scolaire})"


class CoefficientMatiere(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='coefficients')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='coefficients')
    coefficient = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Coefficient'
        verbose_name_plural = 'Coefficients'
        unique_together = ['classe', 'matiere']
    
    def __str__(self):
        return f"{self.matiere.nom} - Coef {self.coefficient} ({self.classe})"


class Attribution(models.Model):
    professeur = models.ForeignKey(ProfilProfesseur, on_delete=models.CASCADE, related_name='attributions')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='attributions')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='attributions')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='attributions')
    
    class Meta:
        verbose_name = 'Attribution'
        verbose_name_plural = 'Attributions'
        unique_together = ['professeur', 'classe', 'matiere', 'annee_scolaire']
    
    def __str__(self):
        return f"{self.professeur} - {self.matiere} ({self.classe})"


class Examen(models.Model):
    nom = models.CharField(max_length=200)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='examens')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='examens')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='examens')
    date_examen = models.DateField()
    duree_minutes = models.PositiveIntegerField(default=60)
    note_sur = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    coefficient = models.PositiveIntegerField(default=1)
    lieu = models.ForeignKey(Salle, on_delete=models.SET_NULL, null=True, blank=True)
    surveillant = models.ForeignKey('authentification.Utilisateur', on_delete=models.SET_NULL, null=True, blank=True)
    est_publie = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Examens'
    
    def __str__(self):
        return f"{self.nom} - {self.classe} - {self.matiere}"


class Epreuve(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='epreuves')
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='epreuves')
    note = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    appreciation = models.TextField(blank=True)
    est_corrige = models.BooleanField(default=False)
    date_correction = models.DateTimeField(null=True, blank=True)
    corrige_par = models.ForeignKey('authentification.Utilisateur', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Épreuve'
        verbose_name_plural = 'Épreuves'
        unique_together = ['examen', 'eleve']
    
    def __str__(self):
        return f"{self.eleve} - {self.examen.nom}"


class Evaluation(models.Model):
    class TypeEval(models.TextChoices):
        INTERROGATION = 'interrogation', 'Interrogation'
        DEVOIR_SURVEILLE = 'devoir', 'Devoir surveillé'
        EXAMEN = 'examen', 'Examen'
        AUTRE = 'autre', 'Autre'

    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='evaluations')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='evaluations')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='evaluations')
    periode = models.ForeignKey(PeriodeEvaluation, on_delete=models.CASCADE, related_name='evaluations')
    type_eval = models.CharField(max_length=20, choices=TypeEval.choices, default=TypeEval.INTERROGATION)
    titre = models.CharField(max_length=200, blank=True)
    note = models.DecimalField(max_digits=5, decimal_places=2)
    coefficient = models.PositiveIntegerField(default=1)
    date_eval = models.DateField()
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
    
    def __str__(self):
        return f"{self.eleve} - {self.matiere}: {self.note}"


class FicheNote(models.Model):
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='fiches_notes')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='fiches_notes')
    periode = models.ForeignKey(PeriodeEvaluation, on_delete=models.CASCADE, related_name='fiches_notes')
    moyenne = models.DecimalField(max_digits=5, decimal_places=2)
    rang = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = 'Fiche de note'
        verbose_name_plural = 'Fiches de notes'
    
    def __str__(self):
        return f"{self.eleve} - {self.periode}"


class ContrainteHoraire(models.Model):
    professeur = models.ForeignKey(ProfilProfesseur, on_delete=models.CASCADE, related_name='contraintes')
    jour = models.CharField(max_length=10)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    type_contrainte = models.CharField(max_length=20)
    statut = models.CharField(max_length=20, default='approuve')
    
    class Meta:
        verbose_name = 'Contrainte horaire'
        verbose_name_plural = 'Contraintes horaires'
    
    def __str__(self):
        return f"{self.professeur} - {self.jour}"
