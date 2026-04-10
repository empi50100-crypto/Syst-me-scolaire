from django.db import models
from django.conf import settings


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


class CoefficientMatiere(models.Model):
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE, related_name='coefficients')
    matiere = models.ForeignKey('Matiere', on_delete=models.CASCADE, related_name='coefficients')
    coefficient = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Coefficient'
        verbose_name_plural = 'Coefficients'
        unique_together = ['classe', 'matiere']
    
    def __str__(self):
        return f"{self.matiere.nom} - Coef {self.coefficient} ({self.classe})"


class Examen(models.Model):
    class TypeExamen(models.TextChoices):
        PREMIER_TRIMESTRE = 'trimestre1', '1er Trimestre'
        DEUXIEME_TRIMESTRE = 'trimestre2', '2ème Trimestre'
        TROISIEME_TRIMESTRE = 'trimestre3', '3ème Trimestre'
        PREMIER_SEMESTRE = 'semestre1', '1er Semestre'
        DEUXIEME_SEMESTRE = 'semestre2', '2ème Semestre'
        EXAMEN_BLANC = 'examen_blanc', 'Examen blanc'
        EXAMEN_FINAL = 'examen_final', 'Examen final'
        CONCOURS = 'concours', 'Concours'
    
    nom = models.CharField(max_length=200)
    type_examen = models.CharField(max_length=20, choices=TypeExamen.choices)
    annee_scolaire = models.ForeignKey('finances.AnneeScolaire', on_delete=models.CASCADE, related_name='examens')
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE, related_name='examens')
    matiere = models.ForeignKey('Matiere', on_delete=models.CASCADE, related_name='examens')
    date_examen = models.DateField()
    duree_minutes = models.PositiveIntegerField(default=60, help_text="Durée en minutes")
    note_sur = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    coefficient = models.PositiveIntegerField(default=1)
    lieu = models.ForeignKey(Salle, on_delete=models.SET_NULL, null=True, blank=True)
    surveillant = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    instructions = models.TextField(blank=True)
    est_publie = models.BooleanField(default=False, verbose_name="Résultats publiés")
    date_publication = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Examens'
        ordering = ['-date_examen']
    
    def __str__(self):
        return f"{self.nom} - {self.classe} - {self.matiere}"


class Epreuve(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='epreuves')
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='epreuves')
    note = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    appreciation = models.TextField(blank=True, help_text="Appréciation du correcteur")
    est_corrige = models.BooleanField(default=False)
    date_correction = models.DateTimeField(null=True, blank=True)
    corrige_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Épreuve'
        verbose_name_plural = 'Épreuves'
        unique_together = ['examen', 'eleve']
    
    def __str__(self):
        return f"{self.eleve} - {self.examen.nom} - {self.note}/20"
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.note is not None:
            self.est_corrige = True
            self.date_correction = timezone.now()
        super().save(*args, **kwargs)


class ContrainteHoraire(models.Model):
    class TypeContrainte(models.TextChoices):
        CONGE = 'conge', 'Congé'
        MALADIE = 'maladie', 'Maladie'
        PERMISSION = 'permission', 'Permission'
        FORMATION = 'formation', 'Formation'
        ABSENCE = 'absence', 'Absence'
        AUTRE = 'autre', 'Autre'
    
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        APPROUVE = 'approuve', 'Approuvé'
        REJETE = 'rejete', 'Rejeté'
    
    professeur = models.ForeignKey('Professeur', on_delete=models.CASCADE, related_name='contraintes')
    jour = models.CharField(max_length=10, choices=[
        ('lundi', 'Lundi'), ('mardi', 'Mardi'), ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'), ('vendredi', 'Vendredi'), ('samedi', 'Samedi')
    ])
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    type_contrainte = models.CharField(max_length=20, choices=TypeContrainte.choices)
    motif = models.TextField(blank=True)
    est_recurrent = models.BooleanField(default=True, help_text="Se répète chaque semaine")
    date_fin = models.DateField(null=True, blank=True, help_text="Pour les contraintes temporaires")
    
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.APPROUVE)
    demande_approuver = models.ForeignKey('accounts.DemandeApprobation', on_delete=models.SET_NULL, null=True, blank=True, related_name='contraintes_approuvees')
    
    class Meta:
        verbose_name = 'Contrainte horaire'
        verbose_name_plural = 'Contraintes horaires'
        ordering = ['professeur', 'jour', 'heure_debut']
    
    def __str__(self):
        return f"{self.professeur} - {self.get_jour_display()} {self.heure_debut}-{self.heure_fin}"


class Classe(models.Model):
    class Niveau(models.TextChoices):
        # Maternelle
        MATERNELLE1 = 'Maternelle1', 'Maternelle 1'
        MATERNELLE2 = 'Maternelle2', 'Maternelle 2'
        # Primaire
        CP1 = 'CP1', 'Cours Préparatoire 1'
        CP2 = 'CP2', 'Cours Préparatoire 2'
        CE1 = 'CE1', 'Cours Élémentaire 1'
        CE2 = 'CE2', 'Cours Élémentaire 2'
        CM1 = 'CM1', 'Cours Moyen 1'
        CM2 = 'CM2', 'Cours Moyen 2'
        # Secondaire 1er cycle
        SIXIEME = '6e', 'Sixième'
        CINQUIEME = '5e', 'Cinquième'
        QUATRIEME = '4e', 'Quatrième'
        TROISIEME = '3e', 'Troisième'
        # Secondaire 2nd cycle
        SECONDE = '2nde', 'Seconde'
        PREMIERE = '1re', 'Première'
        TERMINALE = 'Tle', 'Terminale'
        # Université
        L1 = 'L1', 'Licence 1'
        L2 = 'L2', 'Licence 2'
        L3 = 'L3', 'Licence 3'
        M1 = 'M1', 'Master 1'
        M2 = 'M2', 'Master 2'
        D1 = 'D1', 'Doctorat 1'
        D2 = 'D2', 'Doctorat 2'
        D3 = 'D3', 'Doctorat 3'
    
    class Serie(models.TextChoices):
        # Collège - Tronc commun (6e à 3e)
        TRONC_COMMUN = 'TC', 'Tronc Commun'
        # Lycée - Séries générales
        A1 = 'A1', 'Série A1 - Lettres Langues Arts'
        A2 = 'A2', 'Série A2 - Lettres Sciences Humaines'
        C = 'C', 'Série C - Maths Sciences Physiques'
        D = 'D', 'Série D - Sciences Vie Terre'
        # Lycée - Séries techniques
        G1 = 'G1', 'Série G1 - Sciences économiques et sociales'
        G2 = 'G2', 'Série G2 - Techniques quantitatives de gestion'
        E = 'E', 'Série E - Maths Technologie'
        F = 'F', 'Série F - Sciences Techniques Industrielles'
    
    class Domaine(models.TextChoices):
        # Université
        SCIENCES = 'Sciences', 'Sciences & Technologies'
        SVT = 'SVT', 'Sciences de la Vie et de la Terre'
        ECONOMIE = 'Economie', 'Sciences Économiques & Gestion'
        DROIT = 'Droit', 'Droit & Sciences Politiques'
        LETTRES = 'Lettres', 'Lettres Arts & Sciences Humaines'
        EDUCATION = 'Education', 'Sciences de l\'Éducation'
        SANTE = 'Santé', 'Santé'
        COMMUNICATION = 'Communication', 'Communication & Journalisme'
    
    class NomClasse(models.TextChoices):
        # Maternelle
        MATERNELLE1 = 'Maternelle 1', 'Maternelle 1'
        MATERNELLE2 = 'Maternelle 2', 'Maternelle 2'
        # Primaire
        CP1 = 'CP1', 'CP1'
        CP2 = 'CP2', 'CP2'
        CE1 = 'CE1', 'CE1'
        CE2 = 'CE2', 'CE2'
        CM1 = 'CM1', 'CM1'
        CM2 = 'CM2', 'CM2'
        # Collège
        SIXIEME = '6e', '6e'
        CINQUIEME = '5e', '5e'
        QUATRIEME = '4e', '4e'
        TROISIEME = '3e', '3e'
        # Lycée
        SECONDE = '2nde', '2nde'
        PREMIERE = '1re', '1re'
        TERMINALE = 'Tle', 'Tle'
        # Université
        L1 = 'L1', 'Licence 1'
        L2 = 'L2', 'Licence 2'
        L3 = 'L3', 'Licence 3'
        M1 = 'M1', 'Master 1'
        M2 = 'M2', 'Master 2'
        D1 = 'D1', 'Doctorat 1'
        D2 = 'D2', 'Doctorat 2'
        D3 = 'D3', 'Doctorat 3'
    
    nom = models.CharField(max_length=50, choices=NomClasse.choices, verbose_name="Nom de la classe")
    niveau = models.CharField(max_length=15, choices=Niveau.choices, verbose_name="Niveau")
    serie = models.CharField(max_length=10, choices=Serie.choices, blank=True, verbose_name="Série (Lycée)")
    domaine = models.CharField(max_length=50, choices=Domaine.choices, blank=True, verbose_name="Domaine (Université)")
    subdivision = models.CharField(max_length=50, blank=True, verbose_name="Subdivision (ex: 1, 2, A, B...)")
    annee_scolaire = models.ForeignKey('finances.AnneeScolaire', on_delete=models.CASCADE, related_name='classes')
    capacite = models.PositiveIntegerField(default=40)
    professeur_principal = models.ForeignKey('Professeur', on_delete=models.SET_NULL, null=True, blank=True, related_name='classes_principales')
    note_conduite_base = models.PositiveIntegerField(default=20, help_text="Note de conduite de base sur 20 pour cette classe")
    matieres = models.ManyToManyField('Matiere', through='ClasseMatiere', through_fields=('classe', 'matiere'), related_name='classes')
    eleves = models.ManyToManyField('eleves.Eleve', through='eleves.Inscription', related_name='classes')
    
    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['niveau', 'nom', 'subdivision']
        unique_together = ['nom', 'serie', 'domaine', 'subdivision', 'annee_scolaire']
    
    def __str__(self):
        parts = []
        if self.subdivision:
            parts.append(f"{self.nom}-{self.subdivision}")
        else:
            parts.append(self.nom)
        
        # Ajouter série pour lycée (6e à Tle)
        if self.nom in ['6e', '5e', '4e', '3e', '2nde', '1re', 'Tle']:
            if self.serie:
                parts.append(f"({self.get_serie_display()})")
        
        # Ajouter domaine pour université
        if self.nom in ['L1', 'L2', 'L3', 'M1', 'M2', 'D1', 'D2', 'D3']:
            if self.domaine:
                parts.append(f"({self.get_domaine_display()})")
        
        return " ".join(parts)


class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    coefficient = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} (coef: {self.coefficient})"


class ClasseMatiere(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    coefficient = models.PositiveIntegerField(default=1, verbose_name="Coefficient pour cette classe")
    
    class Meta:
        unique_together = ['classe', 'matiere']
    
    def __str__(self):
        return f"{self.classe} - {self.matiere} (coef: {self.coefficient})"


class Professeur(models.Model):
    class Statut(models.TextChoices):
        ACTIF = 'actif', 'Actif'
        CONGE = 'conge', 'En congé'
        PARTI = 'parti', 'Parti'
    
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, null=True, blank=True, related_name='professeur')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    date_embauche = models.DateField()
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ACTIF)
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    
    class Meta:
        verbose_name = 'Professeur'
        verbose_name_plural = 'Professeurs'
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"Prof. {self.prenom} {self.nom}"


class Enseignement(models.Model):
    class Jour(models.TextChoices):
        LUNDI = 'lundi', 'Lundi'
        MARDI = 'mardi', 'Mardi'
        MERCREDI = 'mercredi', 'Mercredi'
        JEUDI = 'jeudi', 'Jeudi'
        VENDREDI = 'vendredi', 'Vendredi'
        SAMEDI = 'samedi', 'Samedi'
    
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name='enseignants')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='enseignements')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='enseignements')
    annee_scolaire = models.ForeignKey('finances.AnneeScolaire', on_delete=models.CASCADE, related_name='enseignements')
    
    horaires = models.JSONField(default=list, blank=True, help_text="Liste des créneaux horaires [{'jour': 'lundi', 'heure_debut': '10:00', 'heure_fin': '12:00'}]")
    
    class Meta:
        verbose_name = 'Enseignement'
        verbose_name_plural = 'Enseignements'
        unique_together = ['professeur', 'classe', 'annee_scolaire']
        ordering = ['professeur', 'classe', 'matiere']
    
    def __str__(self):
        return f"{self.professeur} - {self.matiere} ({self.classe})"
    
    def get_horaires_display(self):
        if not self.horaires:
            return "Aucun horaire défini"
        jours = dict(self.Jour.choices)
        parts = []
        for h in self.horaires:
            jour = jours.get(h.get('jour', ''), h.get('jour', ''))
            debut = h.get('heure_debut', '')
            fin = h.get('heure_fin', '')
            parts.append(f"{jour} {debut}-{fin}")
        return ", ".join(parts) if parts else "Aucun horaire défini"
    
    @property
    def duree_minutes(self):
        if not self.horaires:
            return 0
        from datetime import datetime
        total = 0
        for h in self.horaires:
            try:
                debut = datetime.strptime(h.get('heure_debut', ''), '%H:%M')
                fin = datetime.strptime(h.get('heure_fin', ''), '%H:%M')
                total += int((fin - debut).total_seconds() / 60)
            except:
                pass
        return total


class Evaluation(models.Model):
    class TypeEval(models.TextChoices):
        INTERROGATION = 'interrogation', 'Interrogation'
        MINI_DEVOIR = 'mini_devoir', 'Mini Devoir'
        DEVOIR = 'devoir', 'Devoir'
        EXAMEN = 'examen', 'Examen'
    
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='evaluations')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='evaluations')
    type_eval = models.CharField(max_length=20, choices=TypeEval.choices)
    titre = models.CharField(max_length=100, blank=True, help_text="Titre de l'évaluation (ex: Interrogation n°1)")
    date_eval = models.DateField()
    note = models.DecimalField(max_digits=5, decimal_places=2)
    coefficient = models.PositiveIntegerField(default=1)
    annee_scolaire = models.ForeignKey('finances.AnneeScolaire', on_delete=models.CASCADE, related_name='evaluations')
    observations = models.TextField(blank=True)
    periode = models.PositiveIntegerField(null=True, blank=True, help_text="Période automatique (1=Trim/Sem1, 2=Trim/Sem2, 3=Trim3)")
    
    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        ordering = ['-date_eval']
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.note is not None:
            if self.note < 0 or self.note > 20:
                raise ValidationError({'note': 'La note doit être comprise entre 0 et 20.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        ordering = ['-date_eval']
    
    def __str__(self):
        titre = f" - {self.titre}" if self.titre else ""
        return f"{self.eleve} - {self.matiere} - {self.get_type_eval_display}{titre} - {self.note}/20"
    
    def calculate_moyenne(self):
        from django.db.models import Avg
        
        evals = Evaluation.objects.filter(
            eleve=self.eleve,
            matiere=self.matiere,
            annee_scolaire=self.annee_scolaire
        )
        
        if not evals.exists():
            return None
        
        total_notes = 0
        total_coef = 0
        
        for eval in evals:
            total_notes += float(eval.note) * eval.coefficient
            total_coef += eval.coefficient
        
        if total_coef > 0:
            return round(total_notes / total_coef, 2)
        return None


class FicheNote(models.Model):
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='fiches_notes')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='fiches_notes')
    cycle = models.ForeignKey('finances.CycleConfig', on_delete=models.CASCADE, related_name='fiches_notes')
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Moyenne calculée automatiquement")
    rang = models.PositiveIntegerField(null=True, blank=True, help_text="Rang dans la classe pour cette matière")
    appreciation = models.TextField(blank=True, help_text="Appréciation du professeur")
    date_saisie = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fiche de note'
        verbose_name_plural = 'Fiches de notes'
        unique_together = ['eleve', 'matiere', 'cycle']
        ordering = ['eleve', 'matiere']
    
    def __str__(self):
        return f"{self.eleve} - {self.matiere} - {self.cycle}"
    
    def calculer_moyenne(self):
        from eleves.models import Inscription
        
        inscriptions = Inscription.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.cycle.annee_scolaire,
            classe__isnull=False
        )
        if not inscriptions.exists():
            return None
        
        classe = inscriptions.first().classe
        
        evals = Evaluation.objects.filter(
            eleve=self.eleve,
            matiere=self.matiere,
            annee_scolaire=self.cycle.annee_scolaire,
            date_eval__gte=self.cycle.date_debut,
            date_eval__lte=self.cycle.date_fin
        )
        
        if not evals.exists():
            return None
        
        grouped_by_type = {}
        for eval in evals:
            if eval.type_eval not in grouped_by_type:
                grouped_by_type[eval.type_eval] = []
            grouped_by_type[eval.type_eval].append(eval)
        
        type_averages = []
        for type_eval, eval_list in grouped_by_type.items():
            notes = [float(e.note) for e in eval_list]
            if notes:
                avg = sum(notes) / len(notes)
                type_averages.append(avg)
        
        if not type_averages:
            return None
        
        coef_matiere = self.matiere.coefficient or 1
        moyenne_sur_20 = sum(type_averages) / len(type_averages)
        moyenne_coef = round(moyenne_sur_20 * coef_matiere, 2)
        
        return {
            'moyenne_sur_20': round(moyenne_sur_20, 2),
            'moyenne_coef': moyenne_coef,
            'coef_matiere': coef_matiere
        }
    
    def save(self, *args, **kwargs):
        result = self.calculer_moyenne()
        if result:
            self.moyenne = result['moyenne_coef']
        else:
            self.moyenne = None
        super().save(*args, **kwargs)
