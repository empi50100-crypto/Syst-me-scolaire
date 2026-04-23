#!/usr/bin/env python
"""
Script pour ajouter des numéros de téléphone aux utilisateurs existants
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentification.models import Utilisateur

def add_telephones_to_users():
    """Ajoute des numéros de téléphone aux utilisateurs qui n'en ont pas"""
    
    # Numéros de téléphone par défaut pour les tests
    telephones_par_defaut = {
        'Admin Super': '+225 01 01 01 01 01',
        'Jean Dupont': '+225 02 02 02 02 02',
        'Marie Martin': '+225 03 03 03 03 03',
        'Pierre Bernard': '+225 04 04 04 04 04',
        'Sophie Petit': '+225 05 05 05 05 05',
        'Lucas Moreau': '+225 06 06 06 06 06',
        'Thomas Roux': '+225 07 07 07 07 07',
        'Emma Garcia': '+225 08 08 08 08 08',
    }
    
    print("📱 Ajout des numéros de téléphone...\n")
    
    updated_count = 0
    
    for user in Utilisateur.objects.all():
        if not user.telephone:
            # Chercher un numéro par défaut basé sur le nom
            nom_complet = user.get_full_name()
            telephone = telephones_par_defaut.get(nom_complet)
            
            # Si pas trouvé, en générer un basé sur l'ID
            if not telephone:
                telephone = f"+225 09 09 09 {user.id:02d}"
            
            user.telephone = telephone
            user.save()
            print(f"✅ {nom_complet or user.username} → {telephone}")
            updated_count += 1
        else:
            print(f"ℹ️ {user.get_full_name() or user.username} → Déjà un téléphone")
    
    print(f"\n📊 Total mis à jour : {updated_count} utilisateurs")
    print(f"📊 Total en base : {Utilisateur.objects.count()} utilisateurs")

if __name__ == '__main__':
    print("=" * 60)
    print("  AJOUT DES TÉLÉPHONES AUX UTILISATEURS")
    print("=" * 60)
    print()
    add_telephones_to_users()
    print()
    print("=" * 60)
    print("  TERMINÉ")
    print("=" * 60)
