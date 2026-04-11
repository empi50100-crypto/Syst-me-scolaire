"""
Management command personnalisée pour créer le super administrateur initial.
Cette commande vérifie qu'aucun super admin n'existe avant de permettre la création.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
import getpass
import os

Utilisateur = get_user_model()


class Command(BaseCommand):
    help = "Créer un super administrateur initial (une seule fois)"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help="Nom d'utilisateur",
        )
        parser.add_argument(
            '--email',
            type=str,
            help="Adresse email",
        )
        parser.add_argument(
            '--password',
            type=str,
            help="Mot de passe",
        )
    
    def handle(self, *args, **options):
        # Vérifier si un super admin existe déjà
        if Utilisateur.objects.filter(role='superadmin').exists():
            raise CommandError(
                "❌ Un super administrateur existe déjà dans le système!\n"
                "Pour des raisons de sécurité, la création de super admins "
                "est désactivée.\n"
                "Contactez l'administrateur système si vous avez besoin d'accès."
            )
        
        # Obtenir les valeurs
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        
        # Mode interactif si aucun argument
        if not username:
            username = input("Nom d'utilisateur: ").strip()
        
        if not email:
            email = input("Adresse email: ").strip()
        
        if not password:
            password = getpass.getpass("Mot de passe: ")
            password_confirm = getpass.getpass("Confirmer le mot de passe: ")
            
            if password != password_confirm:
                raise CommandError("❌ Les mots de passe ne correspondent pas!")
            
            if len(password) < 8:
                raise CommandError("❌ Le mot de passe doit contenir au moins 8 caractères")
        
        # Vérifier que le username n'existe pas
        if Utilisateur.objects.filter(username=username).exists():
            raise CommandError(f"❌ Le nom d'utilisateur '{username}' existe déjà")
        
        # Créer le super admin
        Utilisateur = Utilisateur.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role=Utilisateur.Role.SUPERADMIN
        )
        
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 50))
        self.stdout.write(self.style.SUCCESS("✅ SUPER ADMINISTRATEUR CRÉÉ AVEC SUCCÈS!"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS(f"Username: {username}"))
        self.stdout.write(self.style.SUCCESS(f"Email: {email}"))
        self.stdout.write(self.style.SUCCESS("\n⚠️ IMPORTANT:"))
        self.stdout.write(self.style.WARNING("- Changez ce mot de passe régulièrement"))
        self.stdout.write(self.style.WARNING("- Conservez ce mot de passe en lieu sûr"))
        self.stdout.write(self.style.WARNING("- Supprimez ce script après utilisation"))
