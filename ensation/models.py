from django.db import models
from django.conf import settings


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la matière")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    coefficient = models.DecimalField(max_digits=3, decimal_places=2, default=1, verbose_name="Coefficient")
    description = models.TextField(blank=True, verbose_name="Description")
    est_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom']
        app_label = 'ensation'

    def __str__(self):
        return self.nom


class Salle(models.Model):
    TYPE_SALLE = (
        ('cours', 'Salle de cours'),
        ('bureau', 'Bureau'),
        ('laboratoire', 'Laboratoire'),
        ('sport', 'Salle de sport'),
        ('conference', 'Salle de conférence'),
    )
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom de la salle")
    capacite = models.IntegerField(default=30, verbose_name="Capacité")
    type_salle = models.CharField(max_length=20, choices=TYPE_SALLE, default='cours', verbose_name="Type de salle")
    est_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"
        ordering = ['nom']
        app_label = 'ensation'

    def __str__(self):
        return f"{self.nom} ({self.get_type_salle_display()})"


class Classe(models.Model):
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom de la classe")
    niveau = models.ForeignKey('core.Niveau', on_delete=models.CASCADE, related_name='classes', verbose_name="Niveau")
    effectif_max = models.IntegerField(default=30, verbose_name="Effectif maximum")
    est_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['nom']
        app_label = 'ensation'

    def __str__(self):
        return self.nom


class Attribution(models.Model):
    professeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'professeur'}, related_name='attributions', verbose_name="Professeur")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='attributions', verbose_name="Matière")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='attributions', verbose_name="Classe")

    class Meta:
        verbose_name = "Attribution"
        verbose_name_plural = "Attributions"
        unique_together = [['professeur', 'matiere', 'classe']]
        app_label = 'ensation'

    def __str__(self):
        return f"{self.professeur} - {self.matiere} ({self.classe})"