from django.core.management.base import BaseCommand
from authentification.models import Service, Module, Permission, Utilisateur


class Command(BaseCommand):
    help = 'Initialise les services et modules selon la V2 de l\'architecture'

    def handle(self, *args, **options):
        self.stdout.write('Création des services...')
        
        # Services - Architecture V2
        services_data = [
            {'nom': 'Scolarité', 'code': 'scolarite', 'icon': 'bi bi-people', 'ordre': 1},
            {'nom': 'Enseignement', 'code': 'enseignement', 'icon': 'bi bi-mortarboard', 'ordre': 2},
            {'nom': 'Espace Enseignant', 'code': 'enseignant', 'icon': 'bi bi-book', 'ordre': 3},
            {'nom': 'Présences', 'code': 'presences', 'icon': 'bi bi-clipboard-check', 'ordre': 4},
            {'nom': 'Communication', 'code': 'communication', 'icon': 'bi bi-chat-dots', 'ordre': 5},
            {'nom': 'Finances', 'code': 'finances', 'icon': 'bi bi-currency-dollar', 'ordre': 6},
            {'nom': 'Ressources Humaines', 'code': 'ressources_humaines', 'icon': 'bi bi-person-badge', 'ordre': 7},
            {'nom': 'Rapports', 'code': 'rapports', 'icon': 'bi bi-file-earmark-bar-graph', 'ordre': 8},
            {'nom': 'Configuration', 'code': 'configuration', 'icon': 'bi bi-gear', 'ordre': 9},
            {'nom': 'Administration', 'code': 'administration', 'icon': 'bi bi-shield', 'ordre': 10},
        ]
        
        services = {}
        for s in services_data:
            service, _ = Service.objects.update_or_create(
                code=s['code'],
                defaults={
                    'nom': s['nom'],
                    'icon': s['icon'],
                    'ordre': s['ordre'],
                    'est_actif': True
                }
            )
            services[s['code']] = service
            self.stdout.write(f'  - {service.nom}')
        
        self.stdout.write('\nCréation des modules...')
        
        modules_data = [
            # Scolarité
            {'service': 'scolarite', 'nom': 'Élèves', 'code': 'eleve_list', 'url': '/scolarite/', 'icon': 'bi bi-person-badge', 'ordre': 1},
            {'service': 'scolarite', 'nom': 'Inscriptions', 'code': 'inscriptions', 'url': '/scolarite/inscriptions/', 'icon': 'bi bi-person-plus', 'ordre': 2},
            {'service': 'scolarite', 'nom': 'Sanctions & Récompenses', 'code': 'discipline', 'url': '/scolarite/discipline/', 'icon': 'bi bi-shield-exclamation', 'ordre': 3},
            {'service': 'scolarite', 'nom': 'Clôture Périodes', 'code': 'periode_cloture', 'url': '/scolarite/periodes/cloture/', 'icon': 'bi bi-lock', 'ordre': 4},
            {'service': 'scolarite', 'nom': 'Notes & Périodes', 'code': 'note_cloture', 'url': '/scolarite/notes/cloture/', 'icon': 'bi bi-journal-check', 'ordre': 5},
            {'service': 'scolarite', 'nom': 'Dossiers médicaux', 'code': 'dossiers_medicaux', 'url': '/scolarite/dossiers-medicaux/', 'icon': 'bi bi-heart-pulse', 'ordre': 6},
            {'service': 'scolarite', 'nom': 'Documents', 'code': 'documents_eleve', 'url': '/scolarite/documents/', 'icon': 'bi bi-file-earmark', 'ordre': 7},
            
            # Enseignement
            {'service': 'enseignement', 'nom': 'Classes', 'code': 'classe_list', 'url': '/enseignement/classes/', 'icon': 'bi bi-tag', 'ordre': 1},
            {'service': 'enseignement', 'nom': 'Professeurs', 'code': 'professeur_list', 'url': '/enseignement/professeurs/', 'icon': 'bi bi-person-workspace', 'ordre': 2},
            {'service': 'enseignement', 'nom': 'Matières', 'code': 'matiere_list', 'url': '/enseignement/matieres/', 'icon': 'bi bi-book', 'ordre': 3},
            {'service': 'enseignement', 'nom': 'Salles', 'code': 'salle_list', 'url': '/enseignement/salles/', 'icon': 'bi bi-door-open', 'ordre': 4},
            {'service': 'enseignement', 'nom': 'Examens', 'code': 'examen_list', 'url': '/enseignement/examens/', 'icon': 'bi bi-clipboard-check', 'ordre': 5},
            {'service': 'enseignement', 'nom': 'Contraintes horaires', 'code': 'contrainte_list', 'url': '/enseignement/contraintes/', 'icon': 'bi bi-clock', 'ordre': 6},
            {'service': 'enseignement', 'nom': 'Attributions', 'code': 'attribution_list', 'url': '/enseignement/attributions/', 'icon': 'bi bi-diagram-3', 'ordre': 7},
            
            # Espace Enseignant
            {'service': 'enseignant', 'nom': 'Mes Classes', 'code': 'mes_classes', 'url': '/enseignement/mes-classes/', 'icon': 'bi bi-collection', 'ordre': 1},
            {'service': 'enseignant', 'nom': 'Emplois du temps', 'code': 'emploi_du_temps', 'url': '/enseignement/emploi-du-temps/', 'icon': 'bi bi-calendar-week', 'ordre': 2},
            {'service': 'enseignant', 'nom': 'Mes Séances', 'code': 'mes_seances', 'url': '/presences/mes-seances/', 'icon': 'bi bi-clock-history', 'ordre': 3},
            {'service': 'enseignant', 'nom': 'Saisie Notes', 'code': 'saisie_notes', 'url': '/enseignement/saisie-notes/', 'icon': 'bi bi-pencil-square', 'ordre': 4},
            
            # Présences
            {'service': 'presences', 'nom': 'Appel', 'code': 'presence_list', 'url': '/presences/', 'icon': 'bi bi-check-circle', 'ordre': 1},
            {'service': 'presences', 'nom': 'Statistiques', 'code': 'statistiques_presence', 'url': '/presences/statistiques/', 'icon': 'bi bi-bar-chart', 'ordre': 2},
            {'service': 'presences', 'nom': 'Rapport Retards', 'code': 'rapport_retards', 'url': '/presences/rapport-retards/', 'icon': 'bi bi-exclamation-triangle', 'ordre': 3},
            
            # Communication
            {'service': 'communication', 'nom': 'Notifications', 'code': 'notifications', 'url': '/authentification/notifications/', 'icon': 'bi bi-bell', 'ordre': 1},
            {'service': 'communication', 'nom': 'Messages', 'code': 'messages', 'url': '/authentification/messages/', 'icon': 'bi bi-chat-dots', 'ordre': 2},
            
            # Finances
            {'service': 'finances', 'nom': 'Frais Scolaires', 'code': 'frais', 'url': '/finances/frais/', 'icon': 'bi bi-receipt', 'ordre': 1},
            {'service': 'finances', 'nom': 'Paiements', 'code': 'paiements', 'url': '/finances/paiements/', 'icon': 'bi bi-cash-stack', 'ordre': 2},
            {'service': 'finances', 'nom': 'Tableau de Bord', 'code': 'tableau_bord_financier', 'url': '/finances/tableau-bord/', 'icon': 'bi bi-pie-chart', 'ordre': 3},
            {'service': 'finances', 'nom': 'Caisse', 'code': 'caisse', 'url': '/finances/caisse/', 'icon': 'bi bi-safe2', 'ordre': 4},
            {'service': 'finances', 'nom': 'Charges', 'code': 'charges', 'url': '/finances/charges/', 'icon': 'bi bi-cart', 'ordre': 5},
            {'service': 'finances', 'nom': 'Cycles', 'code': 'cycles', 'url': '/finances/cycles/', 'icon': 'bi bi-calendar-range', 'ordre': 6},
            {'service': 'finances', 'nom': 'Élèves en Retard', 'code': 'eleves_retard', 'url': '/finances/eleves-en-retard/', 'icon': 'bi bi-exclamation-diamond', 'ordre': 7},
            {'service': 'finances', 'nom': 'Factures', 'code': 'factures', 'url': '/finances/factures/', 'icon': 'bi bi-file-earmark-text', 'ordre': 8},
            {'service': 'finances', 'nom': 'Bourses', 'code': 'bourses', 'url': '/finances/bourses/', 'icon': 'bi bi-graduation-cap', 'ordre': 9},
            {'service': 'finances', 'nom': 'Rapports Financiers', 'code': 'rapport_financier', 'url': '/finances/rapport-financier/', 'icon': 'bi bi-graph-up', 'ordre': 10},
            {'service': 'finances', 'nom': 'Rappels', 'code': 'rappels', 'url': '/finances/rappels/', 'icon': 'bi bi-bell-fill', 'ordre': 11},
            
            # Ressources Humaines
            {'service': 'ressources_humaines', 'nom': 'Personnel', 'code': 'personnel_rh', 'url': '/ressources-humaines/', 'icon': 'bi bi-people', 'ordre': 1},
            {'service': 'ressources_humaines', 'nom': 'Salaires', 'code': 'salaires_rh', 'url': '/ressources-humaines/salaires/', 'icon': 'bi bi-cash-stack', 'ordre': 2},
            {'service': 'ressources_humaines', 'nom': 'Postes', 'code': 'postes', 'url': '/ressources-humaines/postes/', 'icon': 'bi bi-briefcase', 'ordre': 3},
            {'service': 'ressources_humaines', 'nom': 'Contrats', 'code': 'contrats', 'url': '/ressources-humaines/contrats/', 'icon': 'bi bi-file-text', 'ordre': 4},
            
            # Configuration
            {'service': 'configuration', 'nom': 'Années scolaires', 'code': 'annee_scolaire', 'url': '/finances/annees/', 'icon': 'bi bi-calendar-event', 'ordre': 1},
            {'service': 'configuration', 'nom': 'Paramètres Core', 'code': 'core_config', 'url': '/admin/core/', 'icon': 'bi bi-gear-fill', 'ordre': 2},
            
            # Administration
            {'service': 'administration', 'nom': 'Utilisateurs', 'code': 'user_list', 'url': '/authentification/users/', 'icon': 'bi bi-person-badge', 'ordre': 1},
            {'service': 'administration', 'nom': 'Journal d\'Audit', 'code': 'audit_log', 'url': '/authentification/journal-audit/', 'icon': 'bi bi-journal-text', 'ordre': 2},
            {'service': 'administration', 'nom': 'Gestion Permissions', 'code': 'permissions_utilisateur', 'url': '/authentification/permissions-utilisateur/', 'icon': 'bi bi-shield-lock', 'ordre': 3},
            {'service': 'administration', 'nom': 'Admin Django', 'code': 'admin_django', 'url': '/admin/', 'icon': 'bi bi-hdd', 'ordre': 4},
            {'service': 'administration', 'nom': 'Approbations', 'code': 'approbations', 'url': '/authentification/demandes/', 'icon': 'bi bi-shield-check', 'ordre': 5},
            
            # Rapports
            {'service': 'rapports', 'nom': 'Bulletins', 'code': 'bulletins', 'url': '/rapports/bulletins/', 'icon': 'bi bi-journal', 'ordre': 1},
            {'service': 'rapports', 'nom': 'Fiches de Notes', 'code': 'fiche_notes', 'url': '/rapports/fiches-notes/', 'icon': 'bi bi-file-text', 'ordre': 2},
            {'service': 'rapports', 'nom': 'Statistiques Globales', 'code': 'stats_globales', 'url': '/rapports/statistiques/', 'icon': 'bi bi-bar-chart', 'ordre': 3},
        ]
        
        for m in modules_data:
            service = services.get(m['service'])
            if service:
                module, _ = Module.objects.update_or_create(
                    code=m['code'],
                    defaults={
                        'service': service,
                        'nom': m['nom'],
                        'url': m['url'],
                        'icon': m['icon'],
                        'ordre': m['ordre'],
                        'est_actif': True
                    }
                )
                self.stdout.write(f'  - {module.nom} ({module.service.nom})')
        
        # Créer les permissions par défaut pour chaque rôle
        self.stdout.write('\nCréation des permissions par rôle...')
        self.create_default_permissions()
        
        self.stdout.write('\nInitialisation terminée avec succès.')
    
    def create_default_permissions(self):
        """Crée les permissions par défaut pour chaque rôle sur tous les modules"""
        from authentification.models import Permission, Module, Utilisateur
        
        # Définition des permissions par rôle
        role_permissions = {
            'superadmin': ['create', 'read', 'update', 'delete', 'export', 'import', 'validate'],
            'direction': ['create', 'read', 'update', 'delete', 'export', 'import', 'validate'],
            'secretaire': ['create', 'read', 'update', 'export'],
            'comptable': ['create', 'read', 'update', 'delete', 'export', 'import'],
            'professeur': ['create', 'read', 'update', 'export'],
            'surveillance': ['read', 'update', 'export'],
            'agent_securite': ['read'],
            'responsable_stock': ['create', 'read', 'update', 'export'],
        }
        
        modules = Module.objects.filter(est_actif=True)
        created_count = 0
        
        for role_code, actions in role_permissions.items():
            for module in modules:
                permission, created = Permission.objects.get_or_create(
                    module=module,
                    role=role_code,
                    defaults={'actions': actions}
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  + {module.nom} -> {role_code}: {actions}')
                else:
                    # Mettre à jour si nécessaire
                    if set(permission.actions) != set(actions):
                        permission.actions = actions
                        permission.save()
        
        self.stdout.write(f'\n{created_count} permissions créées.')
