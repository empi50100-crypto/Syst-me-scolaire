def annee_scolaire_actuelle(request):
    from finances.models import AnneeScolaire
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    return {'annee_scolaire': annee, 'annee': annee, 'annees': annees}


def notification_count(request):
    if request.user.is_authenticated:
        from accounts.models import Notification, Message
        unread_notifications = Notification.objects.filter(destinataire=request.user, est_lu=False).count()
        unread_messages = Message.objects.filter(
            destinataire=request.user,
            est_lu=False,
            type_message=Message.TypeMessage.INDIVIDUEL
        ).count()
        return {'notification_count': unread_notifications, 'unread_notifications_count': unread_notifications, 'unread_messages_count': unread_messages}
    return {'notification_count': 0, 'unread_notifications_count': 0, 'unread_messages_count': 0}
