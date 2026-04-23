#!/usr/bin/env python
"""
Script pour créer automatiquement les fiches de poste correspondant aux fonctions
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ressources_humaines.models import FichePoste

def create_fiches_poste():
    """Crée les fiches de poste par défaut pour chaque fonction"""
    
    postes_data = [
        {
            'titre': 'Directeur/Directrice',
            'description': 'Responsable de la direction générale de l\'établissement. Supervise toutes les activités administratives et pédagogiques.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Secrétaire',
            'description': 'Gère la correspondance, l\'accueil, la documentation et le secrétariat de direction.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Comptable',
            'description': 'Gestion comptable, financière et budgétaire de l\'établissement.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Enseignant',
            'description': 'Responsable de l\'enseignement et de l\'éducation des élèves dans une ou plusieurs matières.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Surveillant',
            'description': 'Supervise la discipline, la sécurité et le comportement des élèves.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Agent de Sécurité',
            'description': 'Assure la sécurité des locaux, du personnel et des élèves.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Responsable Stock',
            'description': 'Gestion des stocks, approvisionnements et inventaire.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Chauffeur',
            'description': 'Conducteur des véhicules de l\'établissement pour le transport scolaire.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Agent d\'entretien / Ménage',
            'description': 'Entretien et nettoyage des locaux de l\'établissement.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Médecin / Infirmier',
            'description': 'Soins médicaux et suivi de la santé des élèves et du personnel.',
            'type_contrat': 'cdi',
        },
        {
            'titre': 'Autre poste',
            'description': 'Poste ne correspondant pas aux catégories standards.',
            'type_contrat': 'cdd',
        },
    ]
    
    created_count = 0
    
    for poste_data in postes_data:
        fiche, created = FichePoste.objects.get_or_create(
            titre=poste_data['titre'],
            defaults={
                'description': poste_data['description'],
                'type_contrat': poste_data['type_contrat'],
                'est_active': True,
            }
        )
        if created:
            print(f"✅ Poste créé : {poste_data['titre']}")
            created_count += 1
        else:
            print(f"ℹ️ Poste existant : {poste_data['titre']}")
    
    print(f"\n📊 Total : {created_count} nouveaux postes créés")
    print(f"📊 Total en base : {FichePoste.objects.count()} postes")

if __name__ == '__main__':
    print("=" * 60)
    print("  CRÉATION DES FICHES DE POSTE")
    print("=" * 60)
    print()
    create_fiches_poste()
    print()
    print("=" * 60)
    print("  TERMINÉ")
    print("=" * 60)
