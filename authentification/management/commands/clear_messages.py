from django.core.management.base import BaseCommand
from authentification.models import Message, Conversation


class Command(BaseCommand):
    help = 'Supprime tous les messages et conversations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirme la suppression',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'ATTENTION: Cette action va supprimer TOUS les messages et conversations!'
                )
            )
            self.stdout.write(
                'Pour confirmer, utilisez: python manage.py clear_messages --confirm'
            )
            return

        # Compter avant suppression
        msg_count = Message.objects.count()
        conv_count = Conversation.objects.count()

        # Supprimer les messages d'abord (car FK vers Conversation)
        Message.objects.all().delete()
        
        # Supprimer les conversations
        Conversation.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Suppression terminée: {msg_count} messages et {conv_count} conversations supprimés.'
            )
        )
