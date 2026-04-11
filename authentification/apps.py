from django.apps import AppConfig


class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentification'
    verbose_name = 'Authentification'
    
    def ready(self):
        import authentification.audit_signals
