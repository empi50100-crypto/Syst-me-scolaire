from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service d'envoi d'emails automatisés"""
    
    @staticmethod
    def send_email(to_emails, subject, html_template, context=None, from_email=None):
        """Envoyer un email avec template HTML"""
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            html_content = render_to_string(html_template, context or {})
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_emails if isinstance(to_emails, list) else [to_emails]
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=False)
            return True
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    @staticmethod
    def send_notification_paiement(payment):
        """Envoyer notification de paiement"""
        if not payment.eleve.email:
            return False
        
        parents = payment.eleve.parenttuteur_set.filter(email__isnull=False)
        if not parents:
            return False
        
        emails = list(parents.values_list('email', flat=True))
        
        return EmailService.send_email(
            to_emails=emails,
            subject=f"Paiement reçu - {payment.eleve.nom_complet}",
            html_template='emails/paiement_recu.html',
            context={
                'eleve': payment.eleve,
                'paiement': payment,
                'montant': f"{payment.montant:,.0f}",
                'date': payment.date_paiement.strftime('%d/%m/%Y')
            }
        )
    
    @staticmethod
    def send_notification_inscription(inscription):
        """Envoyer confirmation d'inscription"""
        if not inscription.eleve.email:
            return False
        
        return EmailService.send_email(
            to_emails=[inscription.eleve.email],
            subject=f"Confirmation d'inscription - {inscription.eleve.nom_complet}",
            html_template='emails/inscription_confirmee.html',
            context={
                'eleve': inscription.eleve,
                'classe': inscription.classe,
                'annee': inscription.annee_scolaire
            }
        )
    
    @staticmethod
    def send_rappel_paiement(eleve, montant_due, date_echeance):
        """Envoyer rappel de paiement"""
        parents = eleve.parenttuteur_set.filter(email__isnull=False)
        if not parents:
            return False
        
        emails = list(parents.values_list('email', flat=True))
        
        return EmailService.send_email(
            to_emails=emails,
            subject=f"Rappel de paiement - {eleve.nom_complet}",
            html_template='emails/rappel_paiement.html',
            context={
                'eleve': eleve,
                'montant': f"{montant_due:,.0f}",
                'date_echeance': date_echeance.strftime('%d/%m/%Y')
            }
        )
    
    @staticmethod
    def send_bulletin(eleve, bulletin_data):
        """Envoyer le bulletin par email"""
        if not eleve.email:
            return False
        
        return EmailService.send_email(
            to_emails=[eleve.email],
            subject=f"Bulletin de notes - {eleve.nom_complet}",
            html_template='emails/bulletin.html',
            context={
                'eleve': eleve,
                'bulletin': bulletin_data
            }
        )
    
    @staticmethod
    def send_welcome_email(user):
        """Envoyer email de bienvenue"""
        return EmailService.send_email(
            to_emails=[user.email],
            subject="Bienvenue sur la plateforme",
            html_template='emails/welcome.html',
            context={
                'user': user,
                'nom': user.get_full_name() or user.username
            }
        )
    
    @staticmethod
    def send_password_reset(user, reset_link):
        """Envoyer lien de réinitialisation"""
        return EmailService.send_email(
            to_emails=[user.email],
            subject="Réinitialisation de votre mot de passe",
            html_template='emails/password_reset.html',
            context={
                'user': user,
                'reset_link': reset_link
            }
        )


class NotificationTask:
    """Tâches de notification programmées"""
    
    @staticmethod
    def send_daily_rappels():
        """Envoyer les rappels quotidiens"""
        from finances.models import Paiement
        from datetime import date, timedelta
        
        # Rechercher les paiements en retard
        echeance = date.today() + timedelta(days=7)
        eleves_en_retard = []  # Logique à implémenter selon les règles métier
        
        for eleve in eleves_en_retard:
            montant = 100000  # À calculer
            EmailService.send_rappel_paiement(eleve, montant, echeance)
    
    @staticmethod
    def send_weekly_bulletins():
        """Envoyer les bulletins hebdomadaire"""
        pass
    
    @staticmethod
    def send_monthly_report():
        """Envoyer le rapport mensuel aux administrateurs"""
        pass