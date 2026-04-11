"""
Bloquer la commande createsuperuser standard pour des raisons de sécurité.
Cette commande remplacée affiche un message d'erreur.
"""
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cette commande a été désactivée pour des raisons de sécurité"
    
    def handle(self, *args, **options):
        raise CommandError(
            "❌ La commande 'createsuperuser' a été désactivée.\n\n"
            "Pour créer un super administrateur initial, utilisez:\n"
            "   python manage.py create_initial_superadmin\n\n"
            "⚠️ Cette commande ne peut être utilisée qu'une seule fois "
            "lors de la configuration initiale du système."
        )