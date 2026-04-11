from django.core.management.base import BaseCommand
from authentification.models import Service, Module, Permission, User


class Command(BaseCommand):
    help = 'Initialise les services et modules'

    def handle(self, *args, **options):
        self.stdout.write('Création des services...')
        
        # Services existants - selon la nouvelle architecture
        services_data = [
            {'nom': 'Scolarité', 'code': 'scolarite', 'icon': 'bi bi-people', 'ordre': 1},
            {'nom': 'Enseignement', 'code': 'academics', 'icon': 'bi bi-mortarboard', 'ordre': 2},
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
            # Scolarité (anciennement Gestion des élèves)
            {'service': 'scolarite', 'nom': 'Élèves', 'code': 'eleve_list', 'url': '/eleves/', 'icon': 'bi bi-person-badge', 'ordre': 1},
            {'service': 'scolarite', 'nom': 'Inscriptions', 'code': 'inscriptions', 'url': '/eleves/inscriptions/', 'icon': 'bi bi-person-plus', 'ordre': 2},
            {'service': 'scolarite', 'nom': 'Discipline', 'code': 'discipline', 'url': '/eleves/discipline/', 'icon': 'bi bi-shield-exclamation', 'ordre': 3},
            {'service': 'scolarite', 'nom': 'Clôture Périodes', 'code': 'periode_cloture', 'url': '/eleves/periodes/cloture/', 'icon': 'bi bi-lock', 'ordre': 4},
            {'service': 'scolarite', 'nom': 'Notes & Périodes', 'code': 'note_cloture', 'url': '/eleves/notes/cloture/', 'icon': 'bi bi-journal-check', 'ordre': 5},
            {'service': 'scolarite', 'nom': 'Dossiers médicaux', 'code': 'dossiers_medicaux', 'url': '/eleves/dossiers-medicaux/', 'icon': 'bi bi-heart-pulse', 'ordre': 6},
            {'service': 'scolarite', 'nom': 'Documents', 'code': 'documents_eleve', 'url': '/eleves/documents/', 'icon': 'bi bi-file-earmark', 'ordre': 7},
            
            # Enseignement (anciennement Gestion Académique)
            {'service': 'academics', 'nom': 'Classes', 'code': 'classe_list', 'url': '/academics/classes/', 'icon': 'bi bi-tag', 'ordre': 1},
            {'service': 'academics', 'nom': 'Professeurs', 'code': 'professeur_list', 'url': '/academics/professeurs/', 'icon': 'bi bi-person-workspace', 'ordre': 2},
            {'service': 'academics', 'nom': 'Matières', 'code': 'matiere_list', 'url': '/academics/matieres/', 'icon': 'bi bi-book', 'ordre': 3},
            {'service': 'academics', 'nom': 'Salles', 'code': 'salle_list', 'url': '/academics/salles/', 'icon': 'bi bi-door-open', 'ordre': 4},
            {'service': 'academics', 'nom': 'Examens', 'code': 'examen_list', 'url': '/academics/examens/', 'icon': 'bi bi-clipboard-check', 'ordre': 5},
            {'service': 'academics', 'nom': 'Contraintes horaires', 'code': 'contrainte_list', 'url': '/academics/contraintes/', 'icon': 'bi bi-clock', 'ordre': 6},
            {'service': 'academics', 'nom': 'Attributions', 'code': 'attribution_list', 'url': '/academics/attributions/', 'icon': 'bi bi-diagram-3', 'ordre': 7},
            
            # Espace Enseignant
            {'service': 'enseignant', 'nom': 'Mes Classes', 'code': 'mes_classes', 'url': '/academics/mes-classes/', 'icon': 'bi bi-collection', 'ordre': 1},
            {'service': 'enseignant', 'nom': 'Emplois du temps', 'code': 'emploi_du_temps', 'url': '/academics/emploi-du-temps/', 'icon': 'bi bi-calendar-week', 'ordre': 2},
            {'service': 'enseignant', 'nom': 'Mes Séances', 'code': 'mes_seances', 'url': '/presences/mes-seances/', 'icon': 'bi bi-clock-history', 'ordre': 3},
            {'service': 'enseignant', 'nom': 'Saisie Notes', 'code': 'saisie_notes', 'url': '/academics/saisie-notes/', 'icon': 'bi bi-pencil-square', 'ordre': 4},
            
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
            
            # Ressources Humaines (NOUVEAU)
            {'service': 'ressources_humaines', 'nom': 'Personnel', 'code': 'personnel_rh', 'url': '/ressources-humaines/', 'icon': 'bi bi-people', 'ordre': 1},
            {'service': 'ressources_humaines', 'nom': 'Salaires', 'code': 'salaires_rh', 'url': '/ressources-humaines/salaires/', 'icon': 'bi bi-cash-stack', 'ordre': 2},
            {'service': 'ressources_humaines', 'nom': 'Postes', 'code': 'postes', 'url': '/ressources-humaines/postes/', 'icon': 'bi bi-briefcase', 'ordre': 3},
            {'service': 'ressources_humaines', 'nom': 'Contrats', 'code': 'contrats', 'url': '/ressources-humaines/contrats/', 'icon': 'bi bi-file-text', 'ordre': 4},
            
            # Configuration
            {'service': 'configuration', 'nom': 'Années scolaires', 'code': 'annee_scolaire', 'url': '/finances/annees/', 'icon': 'bi bi-calendar-event', 'ordre': 1},
            {'service': 'configuration', 'nom': 'Salles', 'code': 'salles_config', 'url': '/configuration/salles/', 'icon': 'bi bi-door-open', 'ordre': 2},
            
            # Administration
            {'service': 'administration', 'nom': 'Utilisateurs', 'code': 'user_list', 'url': '/authentification/utilisateurs/', 'icon': 'bi bi-person-badge', 'ordre': 1},
            {'service': 'administration', 'nom': 'Comptes bloqués', 'code': 'comptes_bloques', 'url': '/authentification/comptes-bloques/', 'icon': 'bi bi-lock-fill', 'ordre': 2},
            {'service': 'administration', 'nom': 'Gestion Permissions', 'code': 'permissions_utilisateur', 'url': '/authentification/permissions-utilisateur/', 'icon': 'bi bi-shield-lock', 'ordre': 3},
            {'service': 'administration', 'nom': 'Demandes Permissions', 'code': 'demandes_permissions', 'url': '/authentification/permissions-modifications/', 'icon': 'bi bi-file-diff', 'ordre': 4},
            {'service': 'administration', 'nom': 'Admin Django', 'code': 'admin_django', 'url': '/admin/', 'icon': 'bi bi-hdd', 'ordre': 5},
            {'service': 'administration', 'nom': 'Rapports', 'code': 'rapport_academique', 'url': '/rapports/academique/', 'icon': 'bi bi-bar-chart', 'ordre': 6},
            {'service': 'administration', 'nom': 'Approbations', 'code': 'approbations', 'url': '/authentification/demandes/', 'icon': 'bi bi-shield-check', 'ordre': 7},
            
            # Rapports
            {'service': 'rapports', 'nom': 'Bulletins', 'code': 'bulletins', 'url': '/rapports/bulletins/', 'icon': 'bi bi-journal', 'ordre': 1},
            {'service': 'rapports', 'nom': 'Fiches de Notes', 'code': 'fiche_notes', 'url': '/rapports/fiches-notes/', 'icon': 'bi bi-file-text', 'ordre': 2},
            {'service': 'rapports', 'nom': 'Rapport Académique', 'code': 'rapport_academique_rapports', 'url': '/rapports/academique/', 'icon': 'bi bi-bar-chart', 'ordre': 3},
            {'service': 'rapports', 'nom': 'Transition Année', 'code': 'transition_annee', 'url': '/rapports/transition-annee/', 'icon': 'bi bi-arrow-repeat', 'ordre': 4},
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
        
        self.stdout.write('\nCréation des permissions par défaut...')
        
        # Permissions par défaut pour chaque rôle
        permissions_data = [
            # Rôle: Super Administrateur - Accès complet
            ('eleve_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('discipline', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('periode_cloture', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('note_cloture', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('fiche_notes', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('bulletins', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('dossiers_medicaux', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('documents_eleve', 'superadmin', ['read', 'write', 'update', 'delete']),
            
            ('classe_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('professeur_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('matiere_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('salle_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('examen_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('contrainte_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('attribution_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            
            ('mes_classes', 'superadmin', ['read']),
            ('emploi_du_temps', 'superadmin', ['read']),
            ('mes_seances', 'superadmin', ['read']),
            ('saisie_notes', 'superadmin', ['read']),
            
            ('presence_list', 'superadmin', ['read', 'write']),
            ('statistiques_presence', 'superadmin', ['read']),
            ('rapport_retards', 'superadmin', ['read']),
            
            # Rôle: Direction - Accès complet
            ('eleve_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('discipline', 'direction', ['read', 'write', 'update', 'delete']),
            ('periode_cloture', 'direction', ['read', 'write', 'update', 'delete']),
            ('note_cloture', 'direction', ['read', 'write', 'update', 'delete']),
            ('fiche_notes', 'direction', ['read', 'write', 'update', 'delete']),
            ('bulletins', 'direction', ['read', 'write', 'update', 'delete']),
            ('dossiers_medicaux', 'direction', ['read', 'write', 'update', 'delete']),
            ('documents_eleve', 'direction', ['read', 'write', 'update', 'delete']),
            
            ('classe_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('professeur_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('matiere_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('salle_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('examen_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('contrainte_list', 'direction', ['read', 'write', 'update', 'delete']),
            ('attribution_list', 'direction', ['read', 'write', 'update', 'delete']),
            
            ('mes_classes', 'direction', ['read']),
            ('emploi_du_temps', 'direction', ['read']),
            ('mes_seances', 'direction', ['read']),
            ('saisie_notes', 'direction', ['read']),
            
            ('presence_list', 'direction', ['read', 'write']),
            ('statistiques_presence', 'direction', ['read']),
            ('rapport_retards', 'direction', ['read']),
            
            # Rôle: Enseignement (Professeur) - Accès limité
            ('fiche_notes', 'professeur', ['read']),
            ('bulletins', 'professeur', ['read']),
            ('examen_list', 'professeur', ['read']),
            ('contrainte_list', 'professeur', ['read', 'write']),
            
            ('mes_classes', 'professeur', ['read']),
            ('emploi_du_temps', 'professeur', ['read']),
            ('mes_seances', 'professeur', ['read', 'write']),
            ('saisie_notes', 'professeur', ['read', 'write']),
            
            ('presence_list', 'professeur', ['read', 'write']),
            ('statistiques_presence', 'professeur', ['read']),
            ('notifications', 'professeur', ['read', 'write']),
            ('messages', 'professeur', ['read', 'write']),
            
            # Rôle: Secrétariat
            ('eleve_list', 'secretaire', ['read', 'write', 'update']),
            ('discipline', 'secretaire', ['read']),
            ('fiche_notes', 'secretaire', ['read']),
            ('bulletins', 'secretaire', ['read']),
            ('dossiers_medicaux', 'secretaire', ['read', 'write']),
            ('documents_eleve', 'secretaire', ['read', 'write']),
            
            ('classe_list', 'secretaire', ['read', 'write', 'update']),
            ('professeur_list', 'secretaire', ['read', 'write', 'update']),
            ('matiere_list', 'secretaire', ['read', 'write', 'update']),
            ('salle_list', 'secretaire', ['read', 'write', 'update']),
            ('examen_list', 'secretaire', ['read', 'write']),
            ('contrainte_list', 'secretaire', ['read']),
            ('attribution_list', 'secretaire', ['read', 'write']),
            
            ('presence_list', 'secretaire', ['read']),
            ('statistiques_presence', 'secretaire', ['read']),
            ('notifications', 'secretaire', ['read', 'write']),
            ('messages', 'secretaire', ['read', 'write']),
            
            # Rôle: Comptabilité
            ('annee_scolaire', 'comptable', ['read']),
            ('notifications', 'comptable', ['read', 'write']),
            ('messages', 'comptable', ['read', 'write']),
            ('fiche_notes', 'comptable', ['read']),
            ('bulletins', 'comptable', ['read']),
            
            # Finances - Comptabilité
            ('frais', 'comptable', ['read', 'write', 'update', 'delete']),
            ('paiements', 'comptable', ['read', 'write', 'update']),
            ('tableau_bord_financier', 'comptable', ['read']),
            ('salaires', 'comptable', ['read', 'write', 'update', 'delete']),
            ('caisse', 'comptable', ['read', 'write', 'update']),
            ('charges', 'comptable', ['read', 'write', 'update', 'delete']),
            ('personnel', 'comptable', ['read', 'write', 'update']),
            ('cycles', 'comptable', ['read', 'write', 'update']),
            ('eleves_retard', 'comptable', ['read']),
            ('factures', 'comptable', ['read', 'write', 'update']),
            ('bourses', 'comptable', ['read', 'write', 'update']),
            ('rapport_financier', 'comptable', ['read']),
            ('rappels', 'comptable', ['read', 'write']),
            
            # Rôle: Surveillance / Contrôle
            ('presence_list', 'surveillance', ['read', 'write']),
            ('statistiques_presence', 'surveillance', ['read']),
            ('rapport_retards', 'surveillance', ['read']),
            ('discipline', 'surveillance', ['read', 'write']),
            ('notifications', 'surveillance', ['read', 'write']),
            ('messages', 'surveillance', ['read', 'write']),
            
            # Rôle: Agent de Sécurité
            ('presence_list', 'agent_securite', ['read']),
            ('statistiques_presence', 'agent_securite', ['read']),
            ('notifications', 'agent_securite', ['read']),
            ('messages', 'agent_securite', ['read']),
            
            # Rôle: Responsable Stock
            ('dossiers_medicaux', 'responsable_stock', ['read']),
            ('documents_eleve', 'responsable_stock', ['read']),
            ('notifications', 'responsable_stock', ['read']),
            ('messages', 'responsable_stock', ['read']),
            
            # Rôle: Chauffeur
            ('presence_list', 'chauffeur', ['read']),
            ('notifications', 'chauffeur', ['read']),
            ('messages', 'chauffeur', ['read']),
            
            # Administration - Superadmin
            ('annee_scolaire', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('user_list', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('comptes_bloques', 'superadmin', ['read', 'write', 'update']),
            ('permissions_utilisateur', 'superadmin', ['read', 'write', 'update', 'delete']),
            ('demandes_permissions', 'superadmin', ['read', 'write', 'update']),
            ('admin_django', 'superadmin', ['read']),
            ('rapport_academique', 'superadmin', ['read']),
            ('approbations', 'superadmin', ['read', 'write', 'update']),
            
            # Administration - Direction
            ('annee_scolaire', 'direction', ['read', 'write', 'update', 'delete']),
            ('user_list', 'direction', ['read', 'write', 'update']),
            ('comptes_bloques', 'direction', ['read', 'write', 'update']),
            ('permissions_utilisateur', 'direction', ['read', 'write', 'update', 'delete']),
            ('demandes_permissions', 'direction', ['read', 'write', 'update']),
            ('rapport_academique', 'direction', ['read']),
            ('approbations', 'direction', ['read', 'write', 'update']),
        ]
        
        for module_code, role, actions in permissions_data:
            module = Module.objects.filter(code=module_code).first()
            if module:
                perm, _ = Permission.objects.update_or_create(
                    module=module,
                    role=role,
                    defaults={'actions': actions}
                )
        
        self.stdout.write('\n--- Initialisation terminee ---\n')
        self.stdout.write(f'Services: {Service.objects.count()}\n')
        self.stdout.write(f'Modules: {Module.objects.count()}\n')
        self.stdout.write(f'Permissions: {Permission.objects.count()}')