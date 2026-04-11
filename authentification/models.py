from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from scolarite.models import Eleve


def log_audit(utilisateur, action, model, obj=None, details='', request=None):
    """Helper function to create audit log entries"""
    from authentification.models import JournalAudit
    
    object_repr = str(obj) if obj else ''
    object_id = obj.pk if obj and hasattr(obj, 'pk') else None
    
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    annee_scolaire = ''
    if hasattr(request, 'annee_active') and request.annee_active:
        annee_scolaire = request.annee_active.libelle
    
    return JournalAudit.objects.create(
        utilisateur=utilisateur,
        action=action,
        model=model,
        object_id=object_id,
        object_repr=object_repr,
        details=details,
        ip_address=ip_address,
        annee_scolaire=annee_scolaire
    )


class JournalAudit(models.Model):
    class Action(models.TextChoices):
        CREATE = 'create', 'Création'
        UPDATE = 'update', 'Modification'
        DELETE = 'delete', 'Suppression'
        VIEW = 'view', 'Consultation'
        LOGIN = 'login', 'Connexion'
        LOGOUT = 'logout', 'Déconnexion'
    
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    model = models.CharField(max_length=50, verbose_name="Modèle")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=255, verbose_name="Objet")
    details = models.TextField(blank=True, verbose_name="Détails")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    annee_scolaire = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date/Heure")
    
    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journal d\'audit'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.utilisateur} - {self.get_action_display()} {self.model} - {self.created_at}"


class Service(models.Model):
    """Services disponibles dans l'application"""
    nom = models.CharField(max_length=100, verbose_name="Nom du service")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, default="bi bi-folder", verbose_name="Icône")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom


class Module(models.Model):
    """Modules/sous-modules accessibles dans l'application"""
    class TypeModule(models.TextChoices):
        MENU = 'menu', 'Menu principal'
        SOUS_MENU = 'sous_menu', 'Sous-menu'
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='modules', verbose_name="Service")
    nom = models.CharField(max_length=100, verbose_name="Nom du module")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code unique")
    url = models.CharField(max_length=200, blank=True, verbose_name="URL")
    icon = models.CharField(max_length=50, default="bi bi-folder", verbose_name="Icône")
    type_module = models.CharField(max_length=20, choices=TypeModule.choices, default=TypeModule.MENU, verbose_name="Type")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sous_modules', verbose_name="Module parent")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['service', 'ordre', 'nom']
    
    def __str__(self):
        return f"{self.service.nom} - {self.nom}"


class Permission(models.Model):
    """Permissions par rôle pour les modules"""
    class Action(models.TextChoices):
        LIRE = 'read', 'Lecture'
        ECRIRE = 'write', 'Écriture'
        MODIFIER = 'update', 'Modification'
        SUPPRIMER = 'delete', 'Suppression'
        ADMIN = 'admin', 'Administration'
    
    class NiveauPermission(models.TextChoices):
        AUCUN = 'aucun', 'Aucun accès'
        LECTURE_SEULE = 'lecture', 'Lecture seule'
        LECTURE_ECRITURE = 'lecture_ecriture', 'Lecture et écriture'
        COMPLET = 'complet', 'Accès complet'
        ADMINISTRATION = 'admin', 'Administration'
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions', verbose_name="Module")
    role = models.CharField(max_length=25, verbose_name="Rôle")
    actions = models.JSONField(default=list, verbose_name="Actions autorisées")
    niveau = models.CharField(max_length=20, choices=NiveauPermission.choices, default=NiveauPermission.LECTURE_SEULE, verbose_name="Niveau de permission")
    require_approval = models.BooleanField(default=False, verbose_name="Exige approbation pour modifications")
    approbateurs = models.JSONField(default=list, verbose_name="Rôles approbateurs")
    
    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        unique_together = ['module', 'role']
    
    def __str__(self):
        return f"{self.module.nom} - {self.role}: {', '.join(self.actions)}"
    
    def can_be_modified_by(self, Utilisateur):
        """Vérifie si l'utilisateur peut modifier cette permission"""
        if Utilisateur.est_superadmin():
            return True
        if Utilisateur.est_direction() and not self.require_approval:
            return True
        if self.require_approval and Utilisateur.role in self.approbateurs:
            return True
        return False


class PermissionModification(models.Model):
    """Demandes de modification de permissions"""
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        APPROUVE = 'approuve', 'Approuvé'
        REJETE = 'rejete', 'Rejeté'
    
    class TypeModification(models.TextChoices):
        AJOUT = 'ajout', 'Ajout'
        MODIFICATION = 'modification', 'Modification'
        SUPPRESSION = 'suppression', 'Suppression'
    
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, null=True, blank=True, related_name='modifications')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name="Module")
    role = models.CharField(max_length=25, verbose_name="Rôle")
    actions_avant = models.JSONField(default=list, verbose_name="Actions avant modification")
    actions_apres = models.JSONField(default=list, verbose_name="Actions après modification")
    niveau_avant = models.CharField(max_length=20, blank=True, verbose_name="Niveau avant")
    niveau_apres = models.CharField(max_length=20, blank=True, verbose_name="Niveau après")
    type_modification = models.CharField(max_length=20, choices=TypeModification.choices, verbose_name="Type de modification")
    motif = models.TextField(verbose_name="Motif de la modification")
    demandeur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='permission_demandes', verbose_name="Demandeur")
    approbateur = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, related_name='permission_approuvees', verbose_name="Approuvé par")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE, verbose_name="Statut")
    date_decision = models.DateTimeField(null=True, blank=True, verbose_name="Date de décision")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire de l'approbateur")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = 'Modification de permission'
        verbose_name_plural = 'Modifications de permissions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type_modification} - {self.module.nom} - {self.role} - {self.statut}"
    
    def approuver(self, approbateur, commentaire=''):
        self.statut = self.Statut.APPROUVE
        self.approbateur = approbateur
        self.commentaire = commentaire
        from django.utils import timezone
        self.date_decision = timezone.now()
        self.save()
        
        # Appliquer la modification
        self._appliquer_modification()
    
    def rejeter(self, approbateur, commentaire=''):
        self.statut = self.Statut.REJETE
        self.approbateur = approbateur
        self.commentaire = commentaire
        from django.utils import timezone
        self.date_decision = timezone.now()
        self.save()
    
    def _appliquer_modification(self):
        if self.type_modification == self.TypeModification.SUPPRESSION:
            Permission.objects.filter(module=self.module, role=self.role).delete()
        else:
            perm, created = Permission.objects.update_or_create(
                module=self.module,
                role=self.role,
                defaults={
                    'actions': self.actions_apres,
                    'niveau': self.niveau_apres
                }
            )


class PermissionPersonnalisee(models.Model):
    """Permissions personnalisées par utilisateur"""
    class NiveauPermission(models.TextChoices):
        AUCUN = 'aucun', 'Aucun accès'
        LECTURE = 'lecture', 'Lecture'
        ECRITURE = 'write', 'Écriture'
        COMPLET = 'complet', 'Complet'
    
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='permissions_modules', verbose_name="Utilisateur")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name="Module")
    actions = models.JSONField(default=list, verbose_name="Actions autorisées")
    niveau = models.CharField(max_length=20, choices=NiveauPermission.choices, default=NiveauPermission.LECTURE, verbose_name="Niveau")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    est_temporaire = models.BooleanField(default=False, verbose_name="Permission temporaire")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, related_name='permissions_crees', verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = 'Permission personnalisée'
        verbose_name_plural = 'Permissions personnalisées'
        unique_together = ['utilisateur', 'module']
    
    def __str__(self):
        return f"{self.utilisateur} - {self.module.nom}: {', '.join(self.actions)}"
    
    def is_valid(self):
        from datetime import date
        if not self.est_actif:
            return False
        if self.est_temporaire:
            today = date.today()
            if self.date_debut and today < self.date_debut:
                return False
            if self.date_fin and today > self.date_fin:
                return False
        return True


class ProfilPermission(models.Model):
    """Profils de permissions réutilisables"""
    nom = models.CharField(max_length=100, verbose_name="Nom du profil de permissions")
    description = models.TextField(blank=True, verbose_name="Description")
    modules = models.ManyToManyField(Module, related_name='profils', verbose_name="Modules autorisés")
    roles_cibles = models.JSONField(default=list, verbose_name="Rôles cibles par défaut")
    
    class Meta:
        verbose_name = 'Profil de permissions'
        verbose_name_plural = 'Profils de permissions'
    
    def __str__(self):
        return self.nom


class Groupe(models.Model):
    class NomGroupe(models.TextChoices):
        DIRECTION = 'direction', 'Direction'
        SECRETARIAT = 'secretaire', 'Secrétariat'
        COMPTABILITE = 'comptable', 'Comptabilité'
        PROFESSEUR = 'professeur', 'Professeur'
        SURVEILLANCE = 'surveillance', 'Surveillance'
    
    nom = models.CharField(max_length=20, choices=NomGroupe.choices, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Groupe'
        verbose_name_plural = 'Groupes'
    
    def __str__(self):
        return self.get_nom_display()


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Super Administrateur'
        DIRECTION = 'direction', 'Direction générale'
        SECRETARIAT = 'secretaire', 'Secrétariat'
        COMPTABILITE = 'comptable', 'Comptabilité'
        PROFESSEUR = 'professeur', 'Enseignement'
        SURVEILLANCE = 'surveillance', 'Contrôle & Supervision'
        AGENT_SECURITE = 'agent_securite', 'Agent de Sécurité'
        RESPONSABLE_STOCK = 'responsable_stock', 'Responsable Stock'
        CHAUFFEUR = 'chauffeur', 'Chauffeur'
    
    role = models.CharField(max_length=25, choices=Role.choices)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    matiere = models.ForeignKey('enseignement.Matiere', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Matière enseignée", related_name="professeurs")
    est_approuve = models.BooleanField(default=False, verbose_name="Compte approuvé")
    
    totp_secret = models.CharField(max_length=32, blank=True, verbose_name="Secret TOTP")
    is_2fa_enabled = models.BooleanField(default=False, verbose_name="Authentification 2FA activée")
    is_2fa_required = models.BooleanField(default=False, verbose_name="2FA obligatoire (Direction/Comptabilité)")
    
    backup_codes = models.JSONField(default=list, blank=True, verbose_name="Codes de secours")
    
    profils_permissions = models.ManyToManyField('ProfilPermission', blank=True, related_name='utilisateurs', verbose_name="Profils de permissions")
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username
    
    @property
    def is_superadmin(self):
        """Propriété pour compatibilité template"""
        return self.role == self.Role.SUPERADMIN or self.is_superuser
    
    def est_superadmin(self):
        return self.is_superadmin
    
    @property
    def is_approved(self):
        """Propriété pour compatibilité template (anglais)"""
        return self.est_approuve
    
    def est_direction(self):
        return self.role == self.Role.DIRECTION
    
    def est_secretaire(self):
        return self.role == self.Role.SECRETARIAT
    
    def est_comptable(self):
        return self.role == self.Role.COMPTABILITE
    
    def est_professeur(self):
        return self.role == self.Role.PROFESSEUR
    
    def est_surveillance(self):
        return self.role == self.Role.SURVEILLANCE
    
    def has_module_permission(self, module_code, action='read'):
        """Vérifie si l'utilisateur a la permission pour un module"""
        from authentification.models import Module, Permission, PermissionPersonnalisee
        
        # Superadmin et direction ont tous les droits par défaut
        if self.est_superadmin() or self.est_direction():
            perm_disabled = PermissionPersonnalisee.objects.filter(
                utilisateur=self,
                module__code=module_code,
                est_actif=False
            ).exists()
            if perm_disabled:
                return False
            return True
        
        # Vérifier les permissions personnalisées par utilisateur (actives)
        perm_user = PermissionPersonnalisee.objects.filter(
            utilisateur=self,
            module__code=module_code,
            est_actif=True
        ).first()
        
        if perm_user and perm_user.is_valid():
            if action in perm_user.actions:
                return True
            else:
                return False
        
        # Vérifier si explicitement désactivé (PermissionPersonnalisee avec est_actif=False)
        perm_disabled = PermissionPersonnalisee.objects.filter(
            utilisateur=self,
            module__code=module_code,
            est_actif=False
        ).exists()
        if perm_disabled:
            return False
        
        # Vérifier permission par rôle
        permission = Permission.objects.filter(module__code=module_code, role=self.role).first()
        if permission and action in permission.actions:
            return True
        
        # Vérifier permissions via profils
        if self.profils_permissions.exists():
            for profil in self.profils_permissions.all():
                if profil.modules.filter(code=module_code).exists():
                    return True
        
        return False
    
    def get_accessible_modules(self, service_code=None):
        """Retourne la liste des modules accessibles pour l'utilisateur"""
        from authentification.models import Module
        
        all_modules = Module.objects.filter(est_actif=True)
        if service_code:
            all_modules = all_modules.filter(service__code=service_code)
        
        accessible = []
        for module in all_modules.select_related('service'):
            if self.has_module_permission(module.code, 'read'):
                accessible.append(module)
        
        return sorted(accessible, key=lambda m: (m.service.ordre, m.ordre))
    
    def get_services_with_modules(self):
        """Retourne les services avec leurs modules accessibles"""
        from authentification.models import Module
        
        accessible_modules = self.get_accessible_modules()
        
        # Grouper par service
        services_data = {}
        for module in accessible_modules:
            service = module.service
            if service.id not in services_data:
                services_data[service.id] = {
                    'service': service,
                    'modules': []
                }
            services_data[service.id]['modules'].append(module)
        
        return sorted(services_data.values(), key=lambda x: x['service'].ordre)
    
    def requires_2fa(self):
        return self.is_2fa_required or self.role in [self.Role.DIRECTION, self.Role.COMPTABILITE, self.Role.SUPERADMIN]
    
    def generate_totp_secret(self):
        import pyotp
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        import pyotp
        if not self.totp_secret:
            self.generate_totp_secret()
        totp = pyotp.TOTP(self.totp_secret)
        return totp.provisioning_uri(name=self.username, issuer_name="Système Scolaire")
    
    def verify_totp(self, token):
        import pyotp
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count=10):
        import secrets
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append({'code': code, 'used': False})
        self.backup_codes = codes
        return codes
    
    def verify_backup_code(self, code):
        for item in self.backup_codes:
            if item['code'] == code.upper() and not item['used']:
                item['used'] = True
                self.save(update_fields=['backup_codes'])
                return True
        return False
    
    def get_remaining_backup_codes(self):
        return sum(1 for item in self.backup_codes if not item['used'])


class Notification(models.Model):
    class TypeNotification(models.TextChoices):
        COMPTE_ATTENTE = 'compte_attente', 'Compte en attente'
        COMPTE_APPROUVE = 'compte_approuve', 'Compte approuvé'
        COMPTE_REFUSE = 'compte_refuse', 'Compte refusé'
        ABSENCE_ELEVE = 'absence_eleve', 'Absence élève'
        RETARD_ELEVE = 'retard_eleve', 'Retard élève'
        DEBUT_COURS = 'debut_cours', 'Début de cours'
        FIN_COURS = 'fin_cours', 'Fin de cours'
        PAIEMENT_RECU = 'paiement_recu', 'Paiement reçu'
        FRAIS_IMPAYE = 'frais_impaye', 'Frais impayé'
        MESSAGE = 'message', 'Nouveau message'
        SECURITE = 'securite', 'Alerte sécurité'
        AUTRE = 'autre', 'Autre'
    
    destinataire = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='notifications')
    expediteur = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications_envoyees')
    type_notification = models.CharField(max_length=30, choices=TypeNotification.choices)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=200, blank=True)
    est_lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire}"
    
    @classmethod
    def creer_notification(cls, destinataire, type_notification, titre, message, expediteur=None, lien=''):
        return cls.objects.create(
            destinataire=destinataire,
            type_notification=type_notification,
            titre=titre,
            message=message,
            expediteur=expediteur,
            lien=lien
        )


class Message(models.Model):
    class TypeMessage(models.TextChoices):
        INDIVIDUEL = 'individuel', 'Message individuel'
        GROUPE = 'groupe', 'Message de groupe'
        SERVICE = 'service', 'Message au service'
    
    auteur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='messages_recus', null=True, blank=True)
    type_message = models.CharField(max_length=20, choices=TypeMessage.choices, default=TypeMessage.INDIVIDUEL)
    service = models.CharField(max_length=20, blank=True, choices=[
        ('direction', 'Direction générale'),
        ('secretaire', 'Secrétariat'),
        ('comptable', 'Comptabilité'),
        ('professeur', 'Enseignement'),
        ('surveillance', 'Contrôle & Supervision'),
    ])
    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    est_lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"{self.sujet} - {self.auteur} -> {self.destinataire}"
    
    @classmethod
    def get_conversations_list(cls, Utilisateur):
        from django.db.models import Max
        sent = cls.objects.filter(auteur=Utilisateur).values('destinataire').annotate(last_msg=Max('date_envoi'))
        received = cls.objects.filter(destinataire=Utilisateur).values('auteur').annotate(last_msg=Max('date_envoi'))
        user_ids = set()
        for item in list(sent) + list(received):
            if 'destinataire' in item:
                user_ids.add(item['destinataire'])
            if 'auteur' in item:
                user_ids.add(item['auteur'])
        user_ids.discard(None)
        return Utilisateur.objects.filter(pk__in=user_ids).order_by('first_name', 'username')
    
    @classmethod
    def get_conversation(cls, user1, user2):
        return cls.objects.filter(
            models.Q(auteur=user1, destinataire=user2) | 
            models.Q(auteur=user2, destinataire=user1)
        ).order_by('date_envoi')


class RoleQuota(models.Model):
    role = models.CharField(max_length=25, unique=True, verbose_name="Rôle")
    max_users = models.PositiveIntegerField(default=1, verbose_name="Nombre max d'utilisateurs")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Quota par rôle"
        verbose_name_plural = "Quotas par rôle"

    def __str__(self):
        role_display = dict(Utilisateur.Role.choices).get(self.role, self.role)
        return f"{role_display}: {self.max_users}"

    @classmethod
    def get_limit(cls, role):
        quota = cls.objects.filter(role=role).first()
        return quota.max_users if quota else None

    @classmethod
    def get_current_count(cls, role):
        return Utilisateur.objects.filter(role=role, is_active=True).count()

    @classmethod
    def can_create_user(cls, role):
        limit = cls.get_limit(role)
        if limit is None:
            return True
        return cls.get_current_count(role) < limit


class TentativeConnexion(models.Model):
    username = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    attempts = models.PositiveIntegerField(default=0)
    lock_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Tentative de connexion'
        verbose_name_plural = 'Tentatives de connexion'
        unique_together = ['username', 'ip_address']

    @classmethod
    def record_failure(cls, username, ip_address):
        from django.utils import timezone
        
        obj, created = cls.objects.get_or_create(
            username=username,
            ip_address=ip_address
        )
        obj.attempts += 1
        
        if obj.attempts >= 5:
            obj.lock_count += 1
            obj.locked_until = timezone.now() + timezone.timedelta(minutes=15 * obj.lock_count)
            obj.attempts = 0
        
        obj.save()
        return obj

    @classmethod
    def reset_attempts(cls, username):
        cls.objects.filter(username=username).delete()


class CodeReinitialisation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Code de réinitialisation'
        verbose_name_plural = 'Codes de réinitialisation'


class DemandeApprobation(models.Model):
    class TypeAction(models.TextChoices):
        CREATION = 'creation', 'Création'
        MODIFICATION = 'modification', 'Modification'
        SUPPRESSION = 'suppression', 'Suppression'
    
    class TypeObjet(models.TextChoices):
        ELEVE = 'eleve', 'Élève'
        DOCUMENT = 'document', 'Document'
        SALAIRE = 'salaire', 'Salaire'
        ENCAISSEMENT = 'encaissement', 'Encaissement'
        DECAISSEMENT = 'decaissement', 'Décaissement'
        PAIEMENT = 'paiement', 'Paiement'
        MATIERE = 'matiere', 'Matière'
        CLASSE = 'classe', 'Classe'
        ATTRIBUTION = 'attribution', 'Attribution matière'
        CONTRAINTE = 'contrainte', 'Contrainte horaire'
        FRAIS = 'frais', 'Frais scolaires'
        EMPLOI_TEMPS = 'emploi_temps', 'Emploi du temps'
        CHARGE = 'charge', 'Charge'
        PERSONNEL = 'personnel', 'Personnel'
        PROFESSEUR = 'professeur', 'Professeur'
        AUTRE = 'autre', 'Autre'
    
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        APPROUVE = 'approuve', 'Approuvé'
        REJETE = 'rejete', 'Rejeté'
    
    demandeur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='demandes_soumises')
    approbateur = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_approuvees')
    type_action = models.CharField(max_length=20, choices=TypeAction.choices)
    type_objet = models.CharField(max_length=20, choices=TypeObjet.choices)
    objet_id = models.PositiveIntegerField(null=True, blank=True)
    objet_repr = models.CharField(max_length=255, verbose_name="Objet concerné")
    details = models.TextField(verbose_name="Détails de la demande")
    details_avant = models.TextField(blank=True, verbose_name="État avant modification")
    details_apos = models.TextField(blank=True, verbose_name="État après modification")
    motif = models.TextField(blank=True, verbose_name="Motif de la demande")
    observations = models.TextField(blank=True, verbose_name="Observations de l'approbateur")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Demande d'approbation"
        verbose_name_plural = "Demandes d'approbation"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.get_type_action_display()} {self.get_type_objet_display()} - {self.demandeur} - {self.get_statut_display()}"


def creer_demande_approbation(demandeur, type_action, type_objet, objet_repr, details, objet_id=None, details_avant='', details_apos='', motif=''):
    """Helper function to create an approval request and notify approvers"""
    from authentification.models import Notification, Utilisateur
    
    demande = DemandeApprobation.objects.create(
        demandeur=demandeur,
        type_action=type_action,
        type_objet=type_objet,
        objet_id=objet_id,
        objet_repr=objet_repr,
        details=details,
        details_avant=details_avant,
        details_apos=details_apos,
        motif=motif
    )
    
    approbateurs = Utilisateur.objects.filter(role__in=[Utilisateur.Role.SUPERADMIN, Utilisateur.Role.DIRECTION], is_active=True)
    
    for approbateur in approbateurs:
        Notification.creer_notification(
            destinataire=approbateur,
            type_notification=Notification.TypeNotification.AUTRE,
            titre=f"Demande d'approbation - {type_objet}",
            message=f"Nouvelle demande de {type_action} {type_objet} de la part de {demandeur.get_full_name() or demandeur.username}.\n\n{details}",
            expediteur=demandeur,
            lien=f'/authentification/demandes/'
        )
    
    return demande
