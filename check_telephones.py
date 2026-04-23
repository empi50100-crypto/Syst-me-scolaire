#!/usr/bin/env python
"""
Script pour vérifier et réparer les numéros de téléphone des utilisateurs
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentification.models import Utilisateur

def check_telephones():
    """Vérifie les numéros de téléphone des utilisateurs"""
    
    print("📱 Vérification des numéros de téléphone...\n")
    
    users = Utilisateur.objects.all()
    total = users.count()
    with_phone = 0
    without_phone = 0
    
    print(f"{'ID':<5} {'Nom':<30} {'Téléphone':<20} {'Rôle':<20}")
    print("-" * 80)
    
    for user in users:
        phone = user.telephone if user.telephone else "❌ NON RENSEIGNÉ"
        name = user.get_full_name() or user.username
        role = user.get_role_display() if hasattr(user, 'get_role_display') else user.role
        
        if user.telephone:
            with_phone += 1
            status = "✅"
        else:
            without_phone += 1
            status = "❌"
        
        print(f"{user.id:<5} {name[:28]:<30} {phone[:18]:<20} {role[:18]:<20}")
    
    print("\n" + "=" * 80)
    print(f"📊 Total utilisateurs : {total}")
    print(f"✅ Avec téléphone : {with_phone} ({with_phone/total*100:.1f}%)")
    print(f"❌ Sans téléphone : {without_phone} ({without_phone/total*100:.1f}%)")
    
    if without_phone > 0:
        print(f"\n⚠️  {without_phone} utilisateurs n'ont pas de numéro de téléphone enregistré.")
        print("   Ces utilisateurs doivent mettre à jour leur profil ou être créés avec un téléphone.")

if __name__ == '__main__':
    print("=" * 80)
    print("  VÉRIFICATION DES TÉLÉPHONES UTILISATEURS")
    print("=" * 80)
    print()
    check_telephones()
    print()
    print("=" * 80)
