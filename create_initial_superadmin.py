"""
Script de création du Super Administrateur initial
À exécuter UNE SEULE FOIS lors de la configuration initiale
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentification.models import User
import getpass

def create_initial_superadmin():
    print("=" * 50)
    print("CRÉATION DU SUPER ADMINISTRATEUR")
    print("=" * 50)
    
    # Vérifier si un super admin existe déjà
    if User.objects.filter(role=User.Role.SUPERADMIN).exists():
        print("❌ Un super administrateur existe déjà!")
        print("Pour des raisons de sécurité,请联系 le développeur.")
        return
    
    # Demander les informations
    print("\nInformations du Super Administrateur:")
    username = input("Nom d'utilisateur: ").strip()
    
    if not username:
        print("❌ Erreur: Le nom d'utilisateur est requis")
        return
    
    # Vérifier que le username n'existe pas
    if User.objects.filter(username=username).exists():
        print(f"❌ Erreur: Le用户名 '{username}' existe déjà")
        return
    
    email = input("Email: ").strip()
    
    # Demander le mot de passe de manière sécurisée
    while True:
        password = getpass.getpass("Mot de passe: ")
        if len(password) < 8:
            print("❌ Le mot de passe doit contenir au moins 8 caractères")
            continue
        
        password_confirm = getpass.getpass("Confirmer le mot de passe: ")
        if password != password_confirm:
            print("❌ Les mots de passe ne correspondent pas")
            continue
        break
    
    # Créer le super admin
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role=User.Role.SUPERADMIN
        )
        
        print("\n" + "=" * 50)
        print("✅ SUPER ADMINISTRATEUR CRÉÉ AVEC SUCCÈS!")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Rôle: Super Administrateur")
        print("\n⚠️  IMPORTANT: Changez ce mot de passe régulièrement!")
        
        # Message de sécurité
        print("\n" + "=" * 50)
        print("SÉCURITÉ")
        print("=" * 50)
        print("Pour sécuriser le système:")
        print("1. Supprimez ce script après utilisation")
        print("2. Désactivez createsuperuser en production")
        print("3. Configurez les permissions des autres utilisateurs")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")

if __name__ == "__main__":
    create_initial_superadmin()