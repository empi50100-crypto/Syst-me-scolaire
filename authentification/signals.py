from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

Utilisateur = get_user_model()


@receiver(post_save, sender=Utilisateur)
def creer_notification_nouveau_compte(sender, instance, created, **kwargs):
    """Créer une notification pour les admin/direction quand un compte est créé en attente"""
    if created and not instance.est_approuve:
        from .models import Notification
        
        # Récupérer tous les utilisateurs ayant le rôle Direction ou SuperAdmin
        admins = Utilisateur.objects.filter(
            is_active=True,
            est_approuve=True
        ).filter(
            role__in=['direction', 'superadmin']
        ) | Utilisateur.objects.filter(
            is_superuser=True,
            is_active=True
        )
        
        # Éliminer les doublons
        admins = admins.distinct()
        
        for admin in admins:
            Notification.creer_notification(
                destinataire=admin,
                type_notification=Notification.TypeNotification.COMPTE_ATTENTE,
                titre='Nouveau compte en attente d\'approbation',
                message=f'Le compte de {instance.get_full_name() or instance.username} ({instance.get_role_display()}) est en attente d\'approbation.',
                lien=f'/authentification/users/',
                expediteur=instance
            )


@receiver(post_save, sender=Utilisateur)
def creer_notification_compte_approuve(sender, instance, created, **kwargs):
    """Créer une notification pour l'utilisateur quand son compte est approuvé"""
    if not created:  # Mise à jour
        # Vérifier si l'utilisateur vient d'être approuvé
        try:
            old_instance = Utilisateur.objects.get(pk=instance.pk)
            if not old_instance.est_approuve and instance.est_approuve:
                # Le compte vient d'être approuvé
                from .models import Notification
                Notification.creer_notification(
                    destinataire=instance,
                    type_notification=Notification.TypeNotification.COMPTE_APPROUVE,
                    titre='Votre compte a été approuvé',
                    message='Votre compte a été approuvé. Vous pouvez maintenant vous connecter et accéder à toutes les fonctionnalités.',
                    lien='/dashboard/'
                )
        except Utilisateur.DoesNotExist:
            pass
