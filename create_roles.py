#!/usr/bin/env python
"""
Crée les comptes pour chaque rôle avec mot de passe 12345
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from authentification.models import Utilisateur

# Définition des comptes par rôle
ROLES = [
    ('direction', 'Direction', 'Jean', 'Dupont'),
    ('secretaire', 'Secretariat', 'Marie', 'Martin'),
    ('comptable', 'Comptabilite', 'Pierre', 'Bernard'),
    ('professeur', 'Professeur', 'Sophie', 'Petit'),
    ('surveillance', 'Surveillance', 'Lucas', 'Moreau'),
    ('agent_securite', 'AgentSecurite', 'Thomas', 'Roux'),
    ('responsable_stock', 'ResponsableStock', 'Emma', 'Garcia'),
]

MOT_DE_PASSE = '12345'

print("=" * 60)
print("CRÉATION DES COMPTES UTILISATEURS PAR RÔLE")
print("=" * 60)
print(f"Mot de passe pour tous: {MOT_DE_PASSE}")
print("=" * 60)

created_users = []

for role_code, role_name, prenom, nom in ROLES:
    username = role_name.lower()
    email = f"{username}@syges-am.com"
    
    try:
        # Supprimer l'ancien utilisateur s'il existe
        Utilisateur.objects.filter(username=username).delete()
        
        # Créer le nouvel utilisateur
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=MOT_DE_PASSE,
            first_name=prenom,
            last_name=nom,
            role=role_code,
            is_staff=True,
            is_active=True,
            est_approuve=True
        )
        created_users.append({
            'username': username,
            'role': role_code,
            'name': f"{prenom} {nom}",
            'email': email
        })
        print(f"✓ {role_name:20s} | {username:20s} | {prenom} {nom}")
        
    except Exception as e:
        print(f"✗ {role_name}: ERREUR - {e}")

print("=" * 60)
print(f"✓ {len(created_users)} comptes créés avec succès")
print("=" * 60)
print("\n📋 RÉCAPITULATIF:")
print("-" * 60)
print(f"{'Username':<25} | {'Rôle':<20} | {'Nom complet'}")
print("-" * 60)
for user in created_users:
    role_display = user['role'].replace('_', ' ').title()
    print(f"{user['username']:<25} | {role_display:<20} | {user['name']}")
print("-" * 60)
print(f"\n🔐 Mot de passe pour tous les comptes: {MOT_DE_PASSE}")
print("=" * 60)
