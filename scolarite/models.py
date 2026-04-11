from django.db import models
from django.conf import settings
from core.models import AnneeScolaire, Cycle, NiveauScolaire, PeriodeEvaluation

class Eleve(models.Model):
    class Statut(models.TextChoices):
        ACTIF = 'actif', 'Actif'
        ANCIEN = 'ancien', 'Ancien'
        SUSPENDU = 'suspendu', 'Suspendu'
        RADIÉ = 'radié', 'Radié'
    
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    adresse = models.TextField()
    telephone_parent = models.CharField(max_length=20, blank=True)
    email_parent = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='scolarite/photos/', blank=True, null=True)
    date_inscription = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ACTIF)
    niveau = models.ForeignKey(NiveauScolaire, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Niveau de classe")
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Élève'
        verbose_name_plural = 'Élèves'
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def save(self, *args, **kwargs):
        if not self.matricule:
            import datetime
            self.matricule = f"ELV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class ParentTuteur(models.Model):
    class LienParente(models.TextChoices):
        PERE = 'pere', 'Père'
        MERE = 'mere', 'Mère'
        TUTEUR = 'tuteur', 'Tuteur légal'
        GRAND_PARENT = 'grand_parent', 'Grand-parent'
        AUTRE = 'autre', 'Autre'
    
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='parents')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    lien_parente = models.CharField(max_length=20, choices=LienParente.choices)
    telephone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name="N° WhatsApp")
    email = models.EmailField(blank=True)
    profession = models.CharField(max_length=100, blank=True)
    adresse = models.TextField(blank=True)
    est_contact_principal = models.BooleanField(default=False, verbose_name="Contact principal")
    
    class Meta:
        verbose_name = 'Parent/Tuteur'
        verbose_name_plural = 'Parents/Tuteurs'
        ordering = ['-est_contact_principal', 'nom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_lien_parente_display()})"


class DossierMedical(models.Model):
    eleve = models.OneToOneField(Eleve, on_delete=models.CASCADE, related_name='dossier_medical')
    groupe_sanguin = models.CharField(max_length=5, blank=True, verbose_name="Groupe sanguin")
    allergies = models.TextField(blank=True, verbose_name="Allergies")
    traitements_en_cours = models.TextField(blank=True, verbose_name="Traitements en cours")
    vaccinations = models.TextField(blank=True, verbose_name="Vaccinations")
    allergies_medicamenteuses = models.TextField(blank=True, verbose_name="Allergies médicamenteuses")
    maladies_chroniques = models.TextField(blank=True, verbose_name="Maladies chroniques")
    contacts_urgence_nom = models.CharField(max_length=100, blank=True, verbose_name="Contact d'urgence (nom)")
    contacts_urgence_tel = models.CharField(max_length=20, blank=True, verbose_name="Contact d'urgence (téléphone)")
    contacts_urgence_lien = models.CharField(max_length=50, blank=True, verbose_name="Lien avec l'élève")
    medecin_traitant = models.CharField(max_length=100, blank=True, verbose_name="Médecin traitant")
    tel_medecin = models.CharField(max_length=20, blank=True, verbose_name="Téléphone médecin")
    observations = models.TextField(blank=True)
    date_derniere_mise_a_jour = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dossier Médical'
        verbose_name_plural = 'Dossiers Médicaux'
    
    def __str__(self):
        return f"Dossier médical - {self.eleve}"


class DocumentEleve(models.Model):
    class TypeDocument(models.TextChoices):
        ACTE_NAISSANCE = 'acte_naissance', 'Acte de naissance'
        CERTIFICAT_SCOLARITE = 'certificat_scolarite', 'Certificat de scolarité'
        CERTIFICAT_MEDICAL = 'certificat_medical', 'Certificat médical'
        PHOTO_IDENTITE = 'photo_identite', 'Photo d\'identité'
        BULLETIN_PRECDENT = 'bulletin_precedent', 'Bulletin précédent'
        AUTRE = 'autre', 'Autre'
    
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=30, choices=TypeDocument.choices)
    fichier = models.FileField(upload_to='scolarite/documents/')
    description = models.CharField(max_length=200, blank=True)
    date_upload = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Document Élève'
        verbose_name_plural = 'Documents Élèves'
        ordering = ['-date_upload']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.eleve}"


class CloturePeriode(models.Model):
    """Clôture des périodes (trimestres/semestres) par le professeur principal"""
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='clotures')
    periode = models.ForeignKey(PeriodeEvaluation, on_delete=models.CASCADE, related_name='clotures')
    date_cloture = models.DateTimeField(auto_now_add=True)
    cloture_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Clôture de période'
        verbose_name_plural = 'Clôtures de périodes'
        unique_together = ['classe', 'periode']
    
    def __str__(self):
        return f"{self.classe.nom} - {self.periode} cloturée"


class ClotureNotes(models.Model):
    """Clôture des notes par matière/professeur pour chaque période"""
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='note_clotures')
    professeur = models.ForeignKey('enseignement.ProfilProfesseur', on_delete=models.CASCADE, related_name='note_clotures')
    periode = models.ForeignKey(PeriodeEvaluation, on_delete=models.CASCADE, related_name='note_clotures')
    date_cloture = models.DateTimeField(auto_now_add=True)
    cloture_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    observations = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Clôture de notes"
        verbose_name_plural = "Clôtures de notes"
        unique_together = ['classe', 'professeur', 'periode']
    
    def __str__(self):
        return f"{self.classe.nom} - {self.professeur} - {self.periode} cloturée"


class SanctionRecompense(models.Model):
    class Type(models.TextChoices):
        SANCTION = 'sanction', 'Sanction'
        RECOMPENSE = 'recompense', 'Récompense'
    
    class TypeSanction(models.TextChoices):
        AVERTISSEMENT = 'avertissement', 'Avertissement'
        BLAME = 'blame', 'Blâme'
        RETENUE = 'retenue', 'Retenue'
        ABSENCE_NON_JUSTIFIEE = 'absence_non_justifiee', 'Absence non justifiée'
        EXCLUSION_TEMPORAIRE = 'exclusion_temporaire', 'Exclusion temporaire'
        EXCLUSION_DEFINITIVE = 'exclusion_definitive', 'Exclusion définitive'
    
    class TypeRecompense(models.TextChoices):
        FELICITATIONS = 'felicitations', 'Félicitations'
        COMMENCEMENT = 'commencement', 'Commencement'
        PRIX_EXCELLENCE = 'prix_excellence', 'Prix d\'excellence'
        MENTION_HONORABLE = 'mention_honorable', 'Mention honorable'
    
    class StatutTraitement(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        TRAITE = 'traite', 'Traité'
    
    class Service(models.TextChoices):
        SURVEILLANCE = 'surveillance', 'Surveillance et Contrôle'
        DIRECTION = 'direction', 'Direction Générale'
        ADMIN = 'admin', 'Administrateur'
    
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='disciplines')
    inscription = models.ForeignKey('EleveInscription', on_delete=models.CASCADE, related_name='disciplines', null=True, blank=True)
    type = models.CharField(max_length=20, choices=Type.choices)
    type_detail = models.CharField(max_length=30)
    description = models.TextField()
    date_incident = models.DateField()
    periode = models.ForeignKey(PeriodeEvaluation, on_delete=models.SET_NULL, null=True, blank=True)
    date_enregistrement = models.DateField(auto_now_add=True)
    enregistre_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    est_signale = models.BooleanField(default=False, verbose_name="Signalé aux parents")
    
    statut_traitement = models.CharField(max_length=20, choices=StatutTraitement.choices, default=StatutTraitement.EN_ATTENTE)
    points = models.IntegerField(default=0, help_text="Points à déduire ou ajouter (- pour sanction, + pour récompense)")
    traite_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='disciplines_traitees')
    service_traitant = models.CharField(max_length=20, choices=Service.choices, blank=True)
    date_traitement = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Sanction/Récompense'
        verbose_name_plural = 'Sanctions/Récompenses'
        ordering = ['-date_incident']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.eleve} ({self.date_incident})"


class EleveInscription(models.Model):
    class Mention(models.TextChoices):
        PASSABLE = 'passable', 'Passable'
        ASSEZ_BIEN = 'assez_bien', 'Assez Bien'
        BIEN = 'bien', 'Bien'
        TRES_BIEN = 'tres_bien', 'Très Bien'
        EXCELLENT = 'excellent', 'Excellent'
    
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='inscriptions')
    classe = models.ForeignKey('enseignement.Classe', on_delete=models.CASCADE, related_name='inscriptions')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='inscriptions')
    date_inscription = models.DateField(auto_now_add=True)
    rang = models.PositiveIntegerField(default=0)
    moyenne_generale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mention = models.CharField(max_length=20, choices=Mention.choices, blank=True)
    decision = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        unique_together = ['eleve', 'annee_scolaire']
        ordering = ['-annee_scolaire__date_debut', 'rang']
    
    def __str__(self):
        return f"{self.eleve} - {self.classe} ({self.annee_scolaire})"


class ConfigurationConduite(models.Model):
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='conduite_configs')
    niveau = models.ForeignKey(NiveauScolaire, on_delete=models.CASCADE, related_name='conduite_configs')
    note_base = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    date_creation = models.DateField(auto_now_add=True)
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Configuration Conduite'
        verbose_name_plural = 'Configurations Conduite'
        unique_together = ['annee_scolaire', 'niveau']
        ordering = ['annee_scolaire', 'niveau']

    def __str__(self):
        return f"{self.niveau}: {self.note_base}/20"


class ConduiteEleve(models.Model):
    inscription = models.ForeignKey(EleveInscription, on_delete=models.CASCADE, related_name='conduites')
    note_base = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    total_deductions = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_recompenses = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    note_finale = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    date_maj = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Conduite Élève'
        verbose_name_plural = 'Conduites Élèves'
        unique_together = ['inscription']

    def __str__(self):
        return f"{self.inscription.eleve}: {self.note_finale}/20"

