from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# List of models to exclude from audit
EXCLUDED_MODELS = ['logentry', 'session', 'migrations', 'auditlog', 'user']


@receiver(post_save)
def audit_save(sender, instance, created, **kwargs):
    """Audit log for create/update operations"""
    # Skip excluded models
    model_name = sender._meta.model_name.lower()
    if model_name in EXCLUDED_MODELS:
        return
    
    # Prevent recursion
    if hasattr(instance, '_audit_in_progress') and instance._audit_in_progress:
        return
    
    instance._audit_in_progress = True
    
    try:
        from accounts.models import AuditLog
        from finances.models import AnneeScolaire
        
        # Get annee_scolaire
        annee_libelle = ''
        try:
            annee = AnneeScolaire.objects.filter(est_active=True).first()
            annee_libelle = annee.libelle if annee else ''
        except:
            pass
        
        AuditLog.objects.create(
            user=None,  # Will be None for admin actions
            action='create' if created else 'update',
            model=f"{sender._meta.app_label}.{sender._meta.model_name}",
            object_repr=str(instance)[:255],
            details=f'{"Création" if created else "Modification"} de {sender._meta.verbose_name}',
            annee_scolaire=annee_libelle
        )
    except Exception:
        pass  # Silently fail
    finally:
        instance._audit_in_progress = False


@receiver(post_delete)
def audit_delete(sender, instance, **kwargs):
    """Audit log for delete operations"""
    # Skip excluded models
    model_name = sender._meta.model_name.lower()
    if model_name in EXCLUDED_MODELS:
        return
    
    # Prevent recursion
    if hasattr(instance, '_audit_in_progress') and instance._audit_in_progress:
        return
    
    instance._audit_in_progress = True
    
    try:
        from accounts.models import AuditLog
        from finances.models import AnneeScolaire
        
        # Get annee_scolaire
        annee_libelle = ''
        try:
            annee = AnneeScolaire.objects.filter(est_active=True).first()
            annee_libelle = annee.libelle if annee else ''
        except:
            pass
        
        AuditLog.objects.create(
            user=None,
            action='delete',
            model=f"{sender._meta.app_label}.{sender._meta.model_name}",
            object_repr=str(instance)[:255],
            details=f'Suppression de {sender._meta.verbose_name}',
            annee_scolaire=annee_libelle
        )
    except Exception:
        pass  # Silently fail
    finally:
        instance._audit_in_progress = False
