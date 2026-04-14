def annee_scolaire_actuelle(request):
    from finances.models import AnneeScolaire
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    return {'annee_scolaire': annee, 'annee': annee, 'annees': annees}


def notification_count(request):
    if request.user.is_authenticated:
        from authentification.models import Notification, Message
        from django.db.models import Q
        unread_notifications = Notification.objects.filter(
            destinataire=request.user,
            est_lu=False
        ).exclude(type_notification=Notification.TypeNotification.MESSAGE).count()
        # Messages individuels non lus
        unread_individual = Message.objects.filter(
            destinataire=request.user,
            est_lu=False,
            type_message=Message.TypeMessage.INDIVIDUEL
        ).count()
        # Messages de groupe non lus (où l'utilisateur est participant mais pas auteur)
        unread_group = Message.objects.filter(
            conversation__participants=request.user,
            est_lu=False,
            type_message=Message.TypeMessage.GROUPE
        ).exclude(auteur=request.user).count()
        # Messages de service non lus - toutes conversations de groupe avec nom commençant par "Service:"
        unread_service = Message.objects.filter(
            Q(conversation__participants=request.user) &
            Q(conversation__is_groupe=True) &
            Q(conversation__nom__startswith='Service:') &
            Q(est_lu=False) &
            Q(type_message='service')
        ).exclude(auteur=request.user).count()
        unread_messages = unread_individual + unread_group + unread_service
        return {'notification_count': unread_notifications, 'unread_notifications_count': unread_notifications, 'unread_messages_count': unread_messages}
    return {'notification_count': 0, 'unread_notifications_count': 0, 'unread_messages_count': 0}
