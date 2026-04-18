#!/usr/bin/env python
"""
Script pour créer des permissions personnalisées pour chaque utilisateur
selon leur rôle. Cela permet à chaque utilisateur d'avoir accès aux modules
nécessaires dans l'interface de permissions.
"""

import os
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from authentification.models import Utilisateur, Permission, PermissionPersonnalisee, Module

# Mapping des modules essentiels par rôle
ROLE_ESSENTIAL_MODULES = {
    'superadmin': [
        'tableau_bord', 'eleve_list', 'inscriptions', 'discipline', 'periode_cloture',
        'note_cloture', 'dossiers_medicaux', 'documents_eleve', 'classe_list',
        'professeur_list', 'matiere_list', 'attribution_list', 'emploi_temps',
        'evaluation_list', 'saisie_notes', 'presence_list', 'paiement_list',
        'frais_scolarite', 'budget', 'rapport_financier', 'rappels', 'bulletin_list',
        'fiche_notes', 'stats_globales', 'personnel_rh', 'salaires_rh', 'postes',
        'contrats', 'annee_scolaire', 'core_config', 'user_list', 'audit_log',
        'permissions_utilisateur', 'admin_django', 'approbations'
    ],
    'direction': [
        'tableau_bord', 'eleve_list', 'inscriptions', 'discipline', 'periode_cloture',
        'note_cloture', 'dossiers_medicaux', 'documents_eleve', 'classe_list',
        'professeur_list', 'matiere_list', 'attribution_list', 'emploi_temps',
        'evaluation_list', 'saisie_notes', 'presence_list', 'paiement_list',
        'frais_scolarite', 'budget', 'rapport_financier', 'rappels', 'bulletin_list',
        'fiche_notes', 'stats_globales', 'personnel_rh', 'salaires_rh', 'postes',
        'contrats', 'annee_scolaire', 'user_list', 'audit_log',
        'permissions_utilisateur', 'approbations'
    ],
    'secretaire': [
        'tableau_bord', 'eleve_list', 'inscriptions', 'discipline',
        'dossiers_medicaux', 'documents_eleve', 'classe_list',
        'professeur_list', 'matiere_list', 'attribution_list', 'emploi_temps',
        'presence_list', 'rappels', 'annee_scolaire', 'user_list', 'approbations'
    ],
    'comptable': [
        'tableau_bord_financier', 'paiement_list', 'frais_scolarite',
        'budget', 'rapport_financier', 'rappels', 'salaires_rh', 'annee_scolaire'
    ],
    'professeur': [
        'tableau_bord', 'eleve_list', 'classe_list',
        'matiere_list', 'emploi_temps', 'evaluation_list', 'saisie_notes',
        'presence_list', 'bulletin_list', 'fiche_notes'
    ],
    'surveillance': [
        'tableau_bord', 'eleve_list', 'classe_list',
        'presence_list', 'discipline', 'rapport_retards', 'statistiques_presence'
    ],
    'agent_securite': [
        'tableau_bord', 'eleve_list', 'presence_list'
    ],
    'responsable_stock': [
        'tableau_bord', 'stock_fournitures', 'stock_livres', 'stock_equipements',
        'mouvements_stock', 'inventaire'
    ],
}

# Actions par défaut par rôle
ROLE_DEFAULT_ACTIONS = {
    'superadmin': ['read', 'create', 'update', 'delete', 'export', 'import', 'validate'],
    'direction': ['read', 'create', 'update', 'delete', 'export', 'import', 'validate'],
    'secretaire': ['read', 'create', 'update', 'export'],
    'comptable': ['read', 'create', 'update', 'delete', 'export', 'import'],
    'professeur': ['read', 'create', 'update', 'export'],
    'surveillance': ['read', 'update', 'export'],
    'agent_securite': ['read'],
    'responsable_stock': ['read', 'create', 'update', 'export'],
}


def create_permissions_for_user(user):
    """Crée les permissions personnalisées pour un utilisateur selon son rôle"""
    role = user.role
    
    # Récupérer les modules essentiels pour ce rôle
    essential_modules = ROLE_ESSENTIAL_MODULES.get(role, [])
    default_actions = ROLE_DEFAULT_ACTIONS.get(role, ['read'])
    
    created_count = 0
    skipped_count = 0
    
    for module_code in essential_modules:
        try:
            module = Module.objects.get(code=module_code)
            
            # Vérifier si une permission existe déjà
            existing = PermissionPersonnalisee.objects.filter(
                utilisateur=user,
                module=module
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Créer la permission personnalisée
            PermissionPersonnalisee.objects.create(
                utilisateur=user,
                module=module,
                actions=default_actions,
                niveau='utilisateur',
                est_actif=True,
                est_temporaire=False
            )
            created_count += 1
            print(f"  ✓ {user.username} -> {module.nom}")
            
        except Module.DoesNotExist:
            print(f"  ✗ Module '{module_code}' introuvable")
            continue
    
    return created_count, skipped_count


def main():
    print("=" * 60)
    print("CRÉATION DES PERMISSIONS PAR RÔLE")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs actifs (sauf superadmin qui a déjà tout)
    users = Utilisateur.objects.filter(is_active=True).exclude(role='superadmin')
    
    total_created = 0
    total_skipped = 0
    
    for user in users:
        print(f"\n{user.username} ({user.get_role_display()}):")
        created, skipped = create_permissions_for_user(user)
        total_created += created
        total_skipped += skipped
        if created == 0 and skipped == 0:
            print(f"  ℹ Aucun module défini pour ce rôle")
    
    print("\n" + "=" * 60)
    print(f"RÉSUMÉ:")
    print(f"  - Permissions créées : {total_created}")
    print(f"  - Permissions existantes (ignorées) : {total_skipped}")
    print(f"  - Total utilisateurs traités : {users.count()}")
    print("=" * 60)


if __name__ == '__main__':
    main()
