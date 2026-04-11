from django.db import models
from core.models import AnneeScolaire


class Presence(models.Model):
    class Statut(models.TextChoices):
        PRESENT = 'present', 'Présent'
        ABSENT = 'absent', 'Absent'
        RETARD = 'retard', 'Retard'
    
    eleve = models.ForeignKey('scolarite.Eleve', on_delete=models.CASCADE, related_name='presences')
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='presences')
    date = models.DateField()
    heure_appel = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices)
    motif_absence = models.TextField(blank=True)
    justifie = models.BooleanField(default=False)
    professeur = models.ForeignKey('enseignement.ProfilProfesseur', on_delete=models.SET_NULL, null=True, blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='presences')
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
        ordering = ['-date', 'eleve__nom']
        unique_together = ['eleve', 'classe', 'date']
    
    def __str__(self):
        return f"{self.eleve} - {self.date} - {self.get_statut_display()}"


class Appel(models.Model):
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='appels')
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField(null=True, blank=True)
    professeur = models.ForeignKey('enseignement.ProfilProfesseur', on_delete=models.SET_NULL, null=True)
    matiere = models.ForeignKey('enseignement.Matiere', on_delete=models.SET_NULL, null=True, blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='appels')
    
    class Meta:
        verbose_name = 'Appel'
        verbose_name_plural = 'Appels'
        unique_together = ['classe', 'date', 'heure_debut']
    
    def __str__(self):
        return f"{self.classe} - {self.date} {self.heure_debut}"


class SeanceCours(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = 'en_cours', 'En cours'
        TERMINEE = 'terminee', 'Terminée'
        ANNULEE = 'annulee', 'Annulée'
    
    professeur = models.ForeignKey('enseignement.ProfilProfesseur', on_delete=models.CASCADE, related_name='seances')
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='seances')
    matiere = models.ForeignKey('enseignement.Matiere', on_delete=models.CASCADE, related_name='seances')
    date = models.DateField()
    heure_debut = models.TimeField(null=True, blank=True)
    heure_fin = models.TimeField(null=True, blank=True)
    duree_minutes = models.IntegerField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_COURS)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='seances')
    notes = models.TextField(blank=True)
    creee_par = models.ForeignKey('authentification.Utilisateur', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Séance de cours'
        verbose_name_plural = 'Séances de cours'
        ordering = ['-date', '-heure_debut']
    
    def __str__(self):
        return f"{self.classe} - {self.matiere} - {self.date} ({self.get_statut_display()})"
