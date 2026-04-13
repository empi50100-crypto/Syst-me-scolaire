from django.db import migrations


def link_existing_messages(apps, schema_editor):
    Message = apps.get_model('authentification', 'Message')
    Conversation = apps.get_model('authentification', 'Conversation')
    
    messages = Message.objects.filter(
        conversation__isnull=True,
        type_message='individuel',
        destinataire__isnull=False
    ).select_related('auteur', 'destinataire')
    
    conv_cache = {}
    for msg in messages:
        key = tuple(sorted([msg.auteur_id, msg.destinataire_id]))
        if key not in conv_cache:
            conv = Conversation.objects.filter(
                participants=msg.auteur
            ).filter(
                participants=msg.destinataire
            ).first()
            if not conv:
                conv = Conversation.objects.create()
                conv.participants.add(msg.auteur, msg.destinataire)
            conv_cache[key] = conv
        else:
            conv = conv_cache[key]
        
        msg.conversation = conv
        msg.save(update_fields=['conversation'])


def unlink_messages(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0003_add_conversation_model'),
    ]

    operations = [
        migrations.RunPython(link_existing_messages, unlink_messages),
    ]
