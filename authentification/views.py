from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import models
from datetime import datetime
import pyotp
import qrcode
import io
import base64
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Utilisateur, log_audit, Notification, Message, TentativeConnexion, ProfilPermission, PermissionPersonnalisee, CodeReinitialisation, Conversation, Groupe
from .forms import UserRegistrationForm, UserCreationForm, UserChangeForm


def send_message_notification(auteur, destinataire, contenu, type_message, conversation=None, message_id=None, refresh_url=None):
    """Diffuse un événement de message sans l'ajouter à la liste des notifications."""
    if not destinataire:
        return

    titre = f"Nouveau message de {auteur.get_full_name() or auteur.username}"
    message_preview = contenu[:100] + "..." if len(contenu) > 100 else contenu
    lien = refresh_url or "/authentification/messages/"
    if not lien and conversation:
        lien = f"/authentification/messages/{conversation.id}/"

    from authentification.consumers import send_message_to_user

    message_data = {
        'type': 'message',
        'titre': titre,
        'message': message_preview,
        'conversation_id': conversation.id if conversation else None,
        'lien': lien,
        'auteur': {
            'id': auteur.id,
            'name': auteur.get_full_name() or auteur.username,
        },
        'date_creation': timezone.now().isoformat()
    }
    
    if message_id:
        message_data['id'] = message_id
    
    if type_message == 'service':
        message_data['type_message'] = 'service'
        message_data['contenu'] = contenu
    
    send_message_to_user(destinataire.id, message_data)


def serialize_chat_message(message):
    return {
        'id': message.id,
        'contenu': message.contenu,
        'auteur': {
            'id': message.auteur_id,
            'name': message.auteur.get_full_name() or message.auteur.username,
        },
        'date_envoi': message.date_envoi.isoformat(),
        'est_lu': message.est_lu,
    }


def broadcast_conversation_message(message):
    if not message.conversation_id:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        f'conversation_{message.conversation_id}',
        {
            'type': 'chat_message',
            'message': serialize_chat_message(message),
            'conversation_id': str(message.conversation_id),
            'sender_id': message.auteur_id
        }
    )


class LoginView(View):
    template_name = 'authentification/login.html'
    two_factor_template = 'authentification/two_factor_login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        if request.session.get('2fa_user_id'):
            return render(request, self.two_factor_template)
        
        response = render(request, self.template_name)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

    @method_decorator(csrf_exempt)
    def post(self, request):
        if request.session.get('2fa_user_id'):
            return self.verify_2fa(request)
        
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Veuillez entrer votre nom d\'utilisateur et mot de passe.')
            return render(request, self.template_name)
        
        attempt_obj = TentativeConnexion.objects.filter(username=username).first()
        if attempt_obj and attempt_obj.locked_until and attempt_obj.locked_until > timezone.now():
            remaining = int((attempt_obj.locked_until - timezone.now()).total_seconds() / 60) + 1
            messages.error(request, f'Compte temporairement bloqué. Réessayez dans {remaining} minute(s).')
            return render(request, self.template_name)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            TentativeConnexion.reset_attempts(username)
            
            if not user.est_approuve and not user.is_superuser and user.role != Utilisateur.Role.DIRECTION:
                messages.error(request, 'Votre compte est en attente de validation par l\'administrateur.')
                return render(request, self.template_name)
            
            if user.is_2fa_enabled and user.totp_secret:
                request.session['2fa_user_id'] = user.id
                request.session['2fa_method'] = 'totp'
                return render(request, self.two_factor_template)
            
            login(request, user)
            log_audit(user, 'login', 'Utilisateur', user, 'Connexion réussie', request)
            messages.success(request, f'Bienvenue, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            ip = self.get_client_ip(request)
            attempt = TentativeConnexion.record_failure(username, ip)
            
            if attempt.locked_until and attempt.locked_until > timezone.now():
                remaining = int((attempt.locked_until - timezone.now()).total_seconds() / 60) + 1
                messages.error(request, f'Compte temporairement bloqué. Réessayez dans {remaining} minute(s).')
            else:
                messages.error(request, f'Nom d\'utilisateur ou mot de passe incorrect. ({5 - attempt.attempts} tentatives restantes)')
            
            return render(request, self.template_name)

    def verify_2fa(self, request):
        user_id = request.session.get('2fa_user_id')
        user = get_object_or_404(Utilisateur, pk=user_id)
        token = request.POST.get('token', '').strip()
        
        if hasattr(user, 'verify_totp') and user.verify_totp(token):
            del request.session['2fa_user_id']
            del request.session['2fa_method']
            login(request, user)
            log_audit(user, 'login', 'Utilisateur', user, 'Connexion 2FA réussie', request)
            messages.success(request, f'Bienvenue, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        
        messages.error(request, 'Code invalide. Veuillez réessayer.')
        return render(request, self.two_factor_template)

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'Vous avez été déconnecté.')
        return redirect('authentification:login')
    
    def post(self, request):
        logout(request)
        messages.info(request, 'Vous avez été déconnecté.')
        return redirect('authentification:login')


class RegisterView(View):
    template_name = 'authentification/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name, {'form': UserRegistrationForm()})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé. Il sera activé après validation.')
            return redirect('authentification:login')
        return render(request, self.template_name, {'form': form})


@login_required
def profile(request):
    return render(request, 'authentification/profile.html')


import random
import string

class PasswordRecoveryView(View):
    template_name = 'authentification/password_recovery.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone')
        
        user = Utilisateur.objects.filter(
            email=email, 
            first_name__iexact=first_name, 
            last_name__iexact=last_name,
            telephone=telephone
        ).first()
        
        if user:
            # Générer un code à 8 chiffres
            code = ''.join(random.choices(string.digits, k=8))
            expires_at = timezone.now() + timezone.timedelta(minutes=15)
            
            CodeReinitialisation.objects.create(
                utilisateur=user,
                code=code,
                expires_at=expires_at
            )
            
            # Dans un cas réel, envoyer l'email ici
            # Pour le test, on pourrait l'afficher ou le stocker en session
            request.session['recovery_email'] = email
            request.session['recovery_user_id'] = user.id
            
            messages.success(request, f"Un code de vérification a été généré (Simulé: {code})")
            return redirect('authentification:password_recovery_verify')
            
        messages.error(request, "Aucun utilisateur trouvé avec ces informations exactes.")
        return render(request, self.template_name)


class PasswordRecoveryVerifyView(View):
    template_name = 'authentification/password_recovery_verify.html'

    def get(self, request):
        email = request.session.get('recovery_email')
        if not email:
            return redirect('authentification:password_recovery')
        return render(request, self.template_name, {'email': email})

    def post(self, request):
        code = request.POST.get('code')
        user_id = request.session.get('recovery_user_id')
        
        if not user_id:
            return redirect('authentification:password_recovery')
            
        reset_code = CodeReinitialisation.objects.filter(
            utilisateur_id=user_id,
            code=code,
            used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if reset_code:
            reset_code.used = True
            reset_code.save()
            request.session['code_verified'] = True
            return redirect('authentification:password_recovery_reset')
            
        messages.error(request, "Code invalide ou expiré.")
        return render(request, self.template_name, {'email': request.session.get('recovery_email')})


class PasswordRecoveryResetView(View):
    template_name = 'authentification/password_recovery_reset.html'

    def get(self, request):
        if not request.session.get('code_verified'):
            return redirect('authentification:password_recovery')
        return render(request, self.template_name)

    def post(self, request):
        if not request.session.get('code_verified'):
            return redirect('authentification:password_recovery')
            
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        username = request.POST.get('username')
        user_id = request.session.get('recovery_user_id')
        
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, self.template_name)
            
        user = get_object_or_404(Utilisateur, pk=user_id)
        user.set_password(password1)
        if username:
            user.username = username
        user.save()
        
        # Nettoyer la session
        request.session.pop('recovery_email', None)
        request.session.pop('recovery_user_id', None)
        request.session.pop('code_verified', None)
        
        messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
        return redirect('authentification:login')


@login_required
def user_list(request):
    if not request.user.has_module_permission("user_list", "read"):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    
    # SuperAdmin voit tous les utilisateurs, les autres ne voient pas les SuperAdmin
    if request.user.is_superadmin:
        users = Utilisateur.objects.all().order_by('-date_joined')
    else:
        users = Utilisateur.objects.exclude(role='superadmin').exclude(is_superuser=True).order_by('-date_joined')
    
    return render(request, 'authentification/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not request.user.has_module_permission("user_list", "write"):
        messages.error(request, "Accès refusé.")
        return redirect('authentification:user_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Utilisateur {user.get_full_name()} créé.')
            return redirect('authentification:user_list')
    else:
        form = UserCreationForm()
    return render(request, 'authentification/user_form.html', {'form': form, 'action': 'Créer'})


@login_required
def user_update(request, pk):
    if not request.user.has_module_permission("user_list", "update"):
        messages.error(request, "Accès refusé.")
        return redirect('authentification:user_list')
    
    user = get_object_or_404(Utilisateur, pk=pk)
    
    # Seul le SuperAdmin peut modifier un SuperAdmin
    if user.is_superadmin and not request.user.is_superadmin:
        messages.error(request, "Vous ne pouvez pas modifier un compte SuperAdmin.")
        return redirect('authentification:user_list')
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur modifié.')
            return redirect('authentification:user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'authentification/user_form.html', {'form': form, 'user_obj': user, 'action': 'Modifier'})


@login_required
def user_delete(request, pk):
    if not request.user.has_module_permission("user_list", "delete"):
        messages.error(request, "Accès refusé.")
        return redirect('authentification:user_list')
    
    user = get_object_or_404(Utilisateur, pk=pk)
    if request.user == user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('authentification:user_list')
    
    if user.is_superadmin:
        messages.error(request, 'Impossible de supprimer un compte SuperAdmin.')
        return redirect('authentification:user_list')
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprimé.')
        return redirect('authentification:user_list')
    return render(request, 'authentification/user_confirm_delete.html', {'user_obj': user})


@login_required
def user_approve(request, pk):
    if not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès refusé.")
        return redirect('authentification:user_list')
    
    user = get_object_or_404(Utilisateur, pk=pk)
    user.est_approuve = True
    user.save()
    messages.success(request, f'Compte de {user.get_full_name()} approuvé.')
    return redirect('authentification:user_list')


@login_required
def user_toggle_active(request, pk):
    if not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès refusé.")
        return redirect('authentification:user_list')
    
    user = get_object_or_404(Utilisateur, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activé' if user.is_active else 'désactivé'
    messages.success(request, f'Utilisateur {user.get_full_name()} {status}.')
    return redirect('authentification:user_list')


@login_required
def notification_list(request):
    filter_type = request.GET.get('filter', 'all')
    notifications = request.user.notifications.exclude(
        type_notification=Notification.TypeNotification.MESSAGE
    ).order_by('-date_creation')
    if filter_type == 'unread':
        notifications = notifications.filter(est_lu=False)
    elif filter_type == 'read':
        notifications = notifications.filter(est_lu=True)
    notifications = notifications[:50]
    return render(request, 'authentification/notification_list.html', {'notifications': notifications, 'filter_type': filter_type})


@login_required
def notification_mark_all_read(request):
    request.user.notifications.exclude(
        type_notification=Notification.TypeNotification.MESSAGE
    ).filter(est_lu=False).update(est_lu=True)
    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
    return redirect('authentification:notification_list')


@login_required
def notification_detail(request, pk):
    from django.shortcuts import get_object_or_404
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    if not notification.est_lu:
        notification.est_lu = True
        notification.save(update_fields=['est_lu'])
    if notification.lien:
        return redirect(notification.lien)
    return redirect('authentification:notification_list')


@login_required
def message_list(request, conversation_id=None):
    filter_type = request.GET.get('filter', 'all')
    conversations_data = []
    total_unread = 0
    
    if filter_type == 'service':
        # Pour Service: afficher TOUTES les conversations de service qui existent
        all_conversations = Conversation.objects.filter(
            is_groupe=True,
            nom__startswith='Service:'
        ).prefetch_related('participants', 'messages')
    elif filter_type == 'groupe':
        # Pour Groupe: afficher toutes les conversations de groupe (mais pas Service)
        all_conversations = Conversation.objects.filter(
            is_groupe=True
        ).exclude(nom__startswith='Service:').prefetch_related('participants', 'messages')
    elif filter_type == 'individuel':
        # Pour Individuel: afficher toutes les conversations non-groupe
        all_conversations = Conversation.objects.filter(
            is_groupe=False
        ).prefetch_related('participants', 'messages')
    else:
        # Pour 'all' (Tous): afficher toutes les conversations de l'utilisateur
        all_conversations = request.user.conversations.all().prefetch_related('participants', 'messages').distinct()
    
    # Traiter chaque conversation
    for conv in all_conversations:
        is_service = conv.is_groupe and conv.nom and conv.nom.startswith('Service:')
        
        # Pour 'all', limiter aux conversations de l'utilisateur
        if filter_type == 'all' and not conv.participants.filter(id=request.user.id).exists():
            continue
            
        last_msg = conv.get_last_message()
        if not last_msg:
            continue
            
        unread = conv.get_unread_count(request.user)
        total_unread += unread
        
        if is_service:
            service_name = conv.nom.replace('Service: ', '')
            service_key = last_msg.service if last_msg.service else 'general'
            conversations_data.append({
                'conversation': conv,
                'other_user': None,
                'last_message': last_msg,
                'unread_count': unread,
                'type': 'service',
                'service_name': service_name,
                'service_key': service_key
            })
        else:
            other = conv.get_other_participant(request.user)
            conversations_data.append({
                'conversation': conv,
                'other_user': other,
                'last_message': last_msg,
                'unread_count': unread,
                'type': 'conversation'
            })
    
    conversations_data.sort(key=lambda x: x['last_message'].date_envoi if x['last_message'] else timezone.now(), reverse=True)
    
    selected_conversation = None
    chat_messages = []
    other_user = None
    display_name = None
    template_name = 'authentification/message_list.html'
    
    if conversation_id:
        try:
            selected_conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            messages.error(request, "Cette conversation n'existe plus.")
            return redirect('authentification:message_list')
        
        if not selected_conversation.participants.filter(id=request.user.id).exists():
            messages.error(request, "Vous n'avez pas accès à cette conversation.")
            return redirect('authentification:message_list')
        else:
            chat_messages = selected_conversation.messages.all().order_by('date_envoi')
            
            # Marquer les messages comme lus selon le type de conversation
            if selected_conversation.is_groupe:
                # Pour les groupes: marquer tous les messages non lus sauf ceux de l'utilisateur
                selected_conversation.messages.filter(est_lu=False).exclude(auteur=request.user).update(est_lu=True)
            else:
                # Pour les conversations individuelles
                selected_conversation.messages.filter(destinataire=request.user, est_lu=False).update(est_lu=True)
            
            other_user = selected_conversation.get_other_participant(request.user)
            display_name = selected_conversation.get_display_name(request.user)
    elif filter_type == 'recus':
        messages_recus_base = request.user.messages_recus.exclude(type_message__in=['service', 'groupe'])
        chat_messages = messages_recus_base.filter(est_lu=False).order_by('-date_envoi')[:50]
    elif filter_type == 'envoyes':
        chat_messages = request.user.messages_envoyes.exclude(type_message__in=['service', 'groupe']).order_by('-date_envoi')[:50]
    elif filter_type == 'individuel':
        # Messages individuels: conversations à deux (pas de groupe)
        chat_messages = Message.objects.filter(
            type_message='individuel'
        ).filter(
            models.Q(auteur=request.user) | models.Q(destinataire=request.user)
        ).order_by('-date_envoi')[:50]
    elif filter_type == 'service':
        # Messages de service: maintenant gérés comme conversations de groupe
        service_conversations = Conversation.objects.filter(
            participants=request.user,
            is_groupe=True,
            nom__startswith='Service:'
        )
        chat_messages = Message.objects.filter(
            conversation__in=service_conversations
        ).order_by('-date_envoi')[:50]
    elif filter_type == 'groupe':
        # Messages de groupe: uniquement des conversations où l'utilisateur participe
        chat_messages = Message.objects.filter(
            type_message='groupe',
            conversation__participants=request.user
        ).exclude(
            auteur=request.user  # Exclure ses propres messages pour voir ceux des autres
        ).order_by('-date_envoi')[:50]
    
    available_users = Utilisateur.objects.filter(is_active=True).exclude(pk=request.user.pk).order_by('first_name', 'username')
    
    return render(request, template_name, {
        'conversations': conversations_data,
        'selected_conversation': selected_conversation,
        'chat_messages': chat_messages,
        'other_user': other_user,
        'display_name': display_name,
        'available_users': available_users,
        'filter_type': filter_type,
        'total_unread': total_unread
    })


@login_required
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.destinataire != request.user and message.auteur != request.user:
        messages.error(request, "Vous n'avez pas accès à ce message.")
        return redirect('authentification:message_list')
    if not message.est_lu and message.destinataire == request.user:
        message.est_lu = True
        message.save(update_fields=['est_lu'])
    if message.conversation:
        return redirect('authentification:message_list', conversation_id=message.conversation.id)
    elif message.destinataire:
        other_user = message.destinataire if message.auteur == request.user else message.auteur
        conversation = Conversation.get_or_create_conversation(request.user, other_user)
        return redirect('authentification:message_list', conversation_id=conversation.id)
    return redirect('authentification:message_list')


@login_required
def message_create(request):
    utilisateurs = Utilisateur.objects.filter(is_active=True).exclude(pk=request.user.pk).order_by('first_name', 'username')
    
    if request.method == 'POST':
        type_message = request.POST.get('type_message', 'individuel')
        contenu = request.POST.get('contenu', '').strip()
        sujet = request.POST.get('sujet', '').strip()
        
        if type_message == 'individuel':
            dest_id = request.POST.get('destinataire')
            if not dest_id:
                messages.error(request, 'Veuillez sélectionner un destinataire.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'individuel'})
            if not contenu:
                messages.error(request, 'Le message ne peut pas être vide.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'individuel'})
            other_user = get_object_or_404(Utilisateur, pk=dest_id)
            conversation = Conversation.get_or_create_conversation(request.user, other_user)
            Message.objects.create(
                auteur=request.user,
                destinataire=other_user,
                conversation=conversation,
                contenu=contenu,
                type_message='individuel'
            )
            send_message_notification(request.user, other_user, contenu, 'individuel', conversation)
            messages.success(request, 'Message envoyé.')
            return redirect('authentification:message_conversation', conversation_id=conversation.id)
        
        elif type_message == 'service':
            service = request.POST.get('service', '')
            if not service:
                messages.error(request, 'Veuillez sélectionner un service.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'service'})
            if not contenu:
                messages.error(request, 'Le message ne peut pas être vide.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'service'})
            
            destinataires_ids = Utilisateur.objects.filter(role=service, is_active=True).values_list('id', flat=True)
            
            if not destinataires_ids.exists():
                messages.error(request, f'Aucun utilisateur trouvé pour le service {service}.')
                return redirect(f"{reverse('authentification:message_list')}?filter=service")
            
            service_name = dict(Utilisateur.Role.choices).get(service, service)
            nom_groupe = f"Service: {service_name}"
            
            participants = [request.user]
            for dest_id in destinataires_ids:
                participants.append(Utilisateur.objects.get(id=dest_id))
            
            conversation = Conversation.create_groupe_conversation(request.user, nom_groupe, participants)
            
            message = Message.objects.create(
                auteur=request.user,
                destinataire=None,
                conversation=conversation,
                contenu=contenu,
                sujet=sujet,
                type_message='service',
                service=service
            )
            
            refresh_url = f"/authentification/messages/{conversation.id}/"
            
            for dest_id in destinataires_ids:
                dest = Utilisateur.objects.get(id=dest_id)
                send_message_notification(request.user, dest, contenu, 'service', conversation, message.id, refresh_url)
            
            messages.success(request, f'Message envoyé à tous les utilisateurs du service.')
            return redirect('authentification:message_conversation', conversation_id=conversation.id)
        
        elif type_message == 'groupe':
            nom_groupe = request.POST.get('nom_groupe', '').strip()
            destinataires_ids = request.POST.getlist('destinataires')
            
            if not nom_groupe:
                messages.error(request, 'Veuillez entrer un nom de groupe.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'groupe'})
            if not destinataires_ids:
                messages.error(request, 'Veuillez sélectionner au moins un participant.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'groupe'})
            if not contenu:
                messages.error(request, 'Le message ne peut pas être vide.')
                return render(request, 'authentification/message_create.html', {'utilisateurs': utilisateurs, 'selected_type': 'groupe'})
            
            groupe, created = Groupe.objects.get_or_create(nom=nom_groupe)
            
            participants = [request.user]
            for dest_id in destinataires_ids:
                participants.append(Utilisateur.objects.get(id=dest_id))
            
            conversation = Conversation.create_groupe_conversation(request.user, nom_groupe, participants)
            
            # Créer UN SEUL message de groupe (pas un par destinataire)
            message = Message.objects.create(
                auteur=request.user,
                destinataire=None,  # Message de groupe : pas de destinataire individuel
                conversation=conversation,
                contenu=contenu,
                sujet=sujet,
                type_message='groupe',
                groupe=groupe
            )
            
            # Envoyer des notifications à tous les participants (sauf l'auteur)
            for dest_id in destinataires_ids:
                dest = Utilisateur.objects.get(id=dest_id)
                send_message_notification(request.user, dest, contenu, 'groupe', conversation)
            
            # Diffuser le message à tous les participants connectés via WebSocket
            broadcast_conversation_message(message)
            
            messages.success(request, f'Message de groupe "{nom_groupe}" envoyé à {len(destinataires_ids)} participants.')
            return redirect('authentification:message_conversation', conversation_id=conversation.id)
        
        messages.error(request, 'Veuillez remplir tous les champs.')
    
    return render(request, 'authentification/message_create.html', {
        'utilisateurs': utilisateurs
    })


@login_required
def message_mark_all_read(request):
    Message.objects.filter(destinataire=request.user, est_lu=False).update(est_lu=True)
    messages.success(request, 'Tous les messages ont été marqués comme lus.')
    return redirect('authentification:message_list')


@login_required
@csrf_exempt
def api_updates(request):
    try:
        last_notification_id = int(request.GET.get('last_notification', 0))
        last_message_id = int(request.GET.get('last_message', 0))
        last_conversation_id = int(request.GET.get('last_conversation', 0))
        mark_notification_read = request.GET.get('mark_notification_read')
        mark_message_read = request.GET.get('mark_message_read')
        
        if mark_notification_read:
            try:
                notification = Notification.objects.get(id=int(mark_notification_read), destinataire=request.user)
                notification.est_lu = True
                notification.save(update_fields=['est_lu'])
            except (Notification.DoesNotExist, ValueError):
                pass
        
        if mark_message_read:
            try:
                message = Message.objects.get(id=int(mark_message_read))
                # Vérifier que l'utilisateur est le destinataire ou un participant de la conversation de groupe
                if message.destinataire == request.user or (
                    message.conversation and 
                    message.conversation.participants.filter(id=request.user.id).exists()
                ):
                    message.est_lu = True
                    message.save(update_fields=['est_lu'])
            except (Message.DoesNotExist, ValueError):
                pass
        
        mark_conversation_read = request.GET.get('mark_conversation_read')
        if mark_conversation_read:
            try:
                conversation = Conversation.objects.get(id=int(mark_conversation_read))
                if conversation.participants.filter(id=request.user.id).exists():
                    # Marquer tous les messages non lus comme lus
                    if conversation.is_groupe:
                        unread = conversation.messages.filter(est_lu=False).exclude(auteur=request.user)
                    else:
                        unread = conversation.messages.filter(destinataire=request.user, est_lu=False)
                    
                    unread_count = unread.count()
                    if unread_count > 0:
                        unread.update(est_lu=True)
                        # Envoyer notification pour mettre à jour le badge
                        from .consumers import send_message_to_user
                        send_message_to_user(request.user.id, {
                            'type': 'messages_read',
                            'conversation_id': conversation.id,
                            'count': unread_count
                        })
            except (Conversation.DoesNotExist, ValueError):
                pass
        
        new_notifications = list(Notification.objects.filter(
            destinataire=request.user,
            est_lu=False,
            id__gt=last_notification_id
        ).exclude(
            type_notification=Notification.TypeNotification.MESSAGE
        ).order_by('-date_creation')[:20])
        
        from django.db.models import Q
        # Messages non lus : individuels OU groupe OU service (où l'utilisateur est participant mais pas auteur)
        new_messages = list(Message.objects.filter(
            Q(
                destinataire=request.user,
                type_message=Message.TypeMessage.INDIVIDUEL
            ) | Q(
                conversation__participants=request.user,
                type_message=Message.TypeMessage.GROUPE,
                auteur__isnull=False
            ) | Q(
                conversation__participants=request.user,
                conversation__is_groupe=True,
                conversation__nom__startswith='Service:',
                type_message=Message.TypeMessage.SERVICE
            ),
            est_lu=False,
            id__gt=last_message_id
        ).exclude(
            auteur=request.user
        ).select_related('auteur', 'conversation').order_by('-date_envoi')[:20])
        
        conversations_qs = request.user.conversations.all().prefetch_related('messages').distinct()
        conversations_data = []
        max_conv_id = last_conversation_id
        all_conversations = []
        
        for conv in conversations_qs.order_by('-updated_at')[:20]:
            if conv.id > last_conversation_id:
                max_conv_id = max(max_conv_id, conv.id)
            
            other = conv.get_other_participant(request.user)
            last_msg = conv.get_last_message()
            unread = conv.get_unread_count(request.user)
            
            if conv.is_groupe:
                conv_data = {
                    'type': 'updated',
                    'id': conv.id,
                    'is_groupe': True,
                    'nom': conv.nom or 'Groupe',
                    'other_user': None,
                    'unread_count': unread,
                    'updated_at': conv.updated_at.isoformat()
                }
            else:
                conv_data = {
                    'type': 'updated',
                    'id': conv.id,
                    'is_groupe': False,
                    'nom': None,
                    'other_user': {
                        'id': other.id,
                        'name': other.get_full_name() or other.username,
                        'avatar': (other.get_full_name()[:1].upper() if other.get_full_name() else other.username[:1].upper())
                    } if other else None,
                    'unread_count': unread,
                    'updated_at': conv.updated_at.isoformat()
                }
            
            if last_msg:
                conv_data['last_message'] = {
                    'id': last_msg.id,
                    'content': last_msg.contenu[:100] if last_msg.contenu else '',
                    'auteur_id': last_msg.auteur_id,
                    'auteur_name': last_msg.auteur.get_full_name() if last_msg.auteur else '',
                    'date_envoi': last_msg.date_envoi.isoformat()
                }
            
            all_conversations.append(conv_data)
        
        notifications_data = []
        for n in new_notifications:
            notifications_data.append({
                'id': n.id,
                'titre': n.titre or '',
                'message': (n.message or '')[:150],
                'type_notification': n.type_notification or '',
                'auteur': {
                    'id': n.expediteur.id if n.expediteur else None,
                    'name': n.expediteur.get_full_name() if n.expediteur else ''
                } if n.expediteur else None,
                'lien': n.lien or '',
                'date_creation': n.date_creation.isoformat()
            })
        
        messages_data = []
        for m in new_messages:
            messages_data.append({
                'id': m.id,
                'contenu': (m.contenu or '')[:100],
                'type_message': m.type_message,
                'auteur': {
                    'id': m.auteur.id,
                    'name': m.auteur.get_full_name() or m.auteur.username
                },
                'conversation_id': m.conversation.id if m.conversation else None,
                'type_message': m.type_message,
                'date_envoi': m.date_envoi.isoformat()
            })
        
        total_notifications = Notification.objects.filter(
            destinataire=request.user,
            est_lu=False
        ).exclude(type_notification=Notification.TypeNotification.MESSAGE).count()
        # Total messages individuels + messages de groupe non lus
        total_individual = Message.objects.filter(
            destinataire=request.user, 
            est_lu=False, 
            type_message=Message.TypeMessage.INDIVIDUEL
        ).count()
        total_group = Message.objects.filter(
            conversation__participants=request.user,
            est_lu=False,
            type_message=Message.TypeMessage.GROUPE
        ).exclude(auteur=request.user).count()
        total_service = Message.objects.filter(
            conversation__participants=request.user,
            conversation__is_groupe=True,
            conversation__nom__startswith='Service:',
            est_lu=False,
            type_message=Message.TypeMessage.SERVICE
        ).exclude(auteur=request.user).count()
        total_messages = total_individual + total_group + total_service
        
        return JsonResponse({
            'notifications': notifications_data,
            'messages': messages_data,
            'conversations': all_conversations,
            'all_conversations': all_conversations,
            'totals': {
                'notifications': total_notifications,
                'messages': total_messages
            },
            'max_conversation_id': max_conv_id,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)


@login_required
def conversation_list(request):
    conversations = request.user.conversations.all().prefetch_related('participants', 'messages').distinct()
    conversations_data = []
    for conv in conversations:
        other = conv.get_other_participant(request.user)
        last_msg = conv.get_last_message()
        unread = conv.get_unread_count(request.user)
        conversations_data.append({
            'conversation': conv,
            'other_user': other,
            'last_message': last_msg,
            'unread_count': unread
        })
    conversations_data.sort(key=lambda x: x['last_message'].date_envoi if x['last_message'] else x['conversation'].updated_at, reverse=True)
    
    available_users = Utilisateur.objects.filter(is_active=True).exclude(pk=request.user.pk).order_by('first_name', 'username')
    
    return render(request, 'authentification/conversation_list.html', {
        'conversations': conversations_data,
        'available_users': available_users
    })


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if not conversation.participants.filter(id=request.user.id).exists():
        messages.error(request, "Vous n'avez pas accès à cette conversation.")
        return redirect('authentification:conversation_list')
    
    messages_conv = conversation.messages.all().order_by('date_envoi')
    
    # Marquer les messages comme lus
    if conversation.is_groupe:
        # Pour les groupes: marquer tous les messages non lus où l'utilisateur n'est pas l'auteur
        unread_messages = conversation.messages.filter(est_lu=False).exclude(auteur=request.user)
    else:
        # Pour les conversations individuelles
        unread_messages = conversation.messages.filter(destinataire=request.user, est_lu=False)
    
    unread_count = unread_messages.count()
    if unread_count > 0:
        unread_messages.update(est_lu=True)
        # Envoyer une notification WebSocket pour mettre à jour le badge en temps réel
        from .consumers import send_message_to_user
        send_message_to_user(request.user.id, {
            'type': 'messages_read',
            'conversation_id': conversation.id,
            'count': unread_count
        })
    
    other_user = conversation.get_other_participant(request.user)
    
    return render(request, 'authentification/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_conv,
        'other_user': other_user
    })


@login_required
def conversation_start(request, user_id):
    other_user = get_object_or_404(Utilisateur, pk=user_id)
    conversation = Conversation.get_or_create_conversation(request.user, other_user)
    return redirect('authentification:message_conversation', conversation_id=conversation.id)


@login_required
def conversation_send(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if not conversation.participants.filter(id=request.user.id).exists():
            return JsonResponse({'error': "Accès refusé"}, status=403)
        
        contenu = request.POST.get('message', '').strip()
        if not contenu:
            return JsonResponse({'error': 'Message vide'}, status=400)
        
        if conversation.is_groupe:
            message = Message.objects.create(
                auteur=request.user,
                conversation=conversation,
                contenu=contenu,
                type_message='groupe'
            )
            conversation.updated_at = message.date_envoi
            conversation.save(update_fields=['updated_at'])
            for participant in conversation.participants.exclude(id=request.user.id):
                send_message_notification(request.user, participant, contenu, 'groupe', conversation)
        else:
            other_user = conversation.get_other_participant(request.user)
            if other_user:
                message = Message.objects.create(
                    auteur=request.user,
                    destinataire=other_user,
                    conversation=conversation,
                    contenu=contenu,
                    type_message='individuel'
                )
                conversation.updated_at = message.date_envoi
                conversation.save(update_fields=['updated_at'])
                send_message_notification(request.user, other_user, contenu, 'individuel', conversation)
            else:
                return JsonResponse({'error': 'Destinataire non trouvé'}, status=400)

        message = Message.objects.select_related('auteur').get(pk=message.pk)
        broadcast_conversation_message(message)
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'date_envoi': message.date_envoi.isoformat(),
            'message': serialize_chat_message(message),
            'conversation_id': conversation.id
        })
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@login_required
def user_permissions_detail(request, pk):
    if not request.user.is_superadmin:
        messages.error(request, "Vous n'avez pas l'autorisation de gérer les permissions.")
        return redirect('authentification:user_list')
    
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        # Mise à jour des permissions personnalisées
        from .models import Module
        permission_codes = request.POST.getlist('permissions')
        
        # Supprimer les anciennes permissions
        PermissionPersonnalisee.objects.filter(utilisateur=utilisateur).delete()
        
        # Créer les nouvelles permissions
        for code in permission_codes:
            try:
                module = Module.objects.get(code=code)
                # Construire la liste des actions
                actions = []
                perm_value = request.POST.get(f'perm_{code}', '')
                if 'lecture' in perm_value:
                    actions.append('read')
                if 'creation' in perm_value:
                    actions.append('create')
                if 'modification' in perm_value:
                    actions.append('update')
                if 'suppression' in perm_value:
                    actions.append('delete')
                
                if actions:
                    PermissionPersonnalisee.objects.create(
                        utilisateur=utilisateur,
                        module=module,
                        actions=actions,
                        niveau='utilisateur',
                        est_actif=True
                    )
            except Module.DoesNotExist:
                continue
        
        messages.success(request, f'Permissions de {utilisateur.get_full_name()} mises à jour.')
        return redirect('authentification:user_list')
    
    # Récupérer les permissions actuelles
    permissions_existantes = {
        p.module.code: p for p in PermissionPersonnalisee.objects.filter(utilisateur=utilisateur).select_related('module')
    }
    
    # Pour superadmin/direction, simuler des permissions complètes si pas de custom permissions
    is_superadmin_or_direction = utilisateur.est_superadmin() or utilisateur.est_direction()
    
    # Liste des modules où l'utilisateur a une permission personnalisée active
    custom_active_modules = set()
    # Liste des modules où l'utilisateur a une permission personnalisée inactive (désactivée)
    custom_disabled_modules = set()
    
    for code, perm in permissions_existantes.items():
        if perm.est_actif:
            custom_active_modules.add(code)
        else:
            custom_disabled_modules.add(code)
    
    # Modules disponibles
    modules_disponibles = [
        {'code': 'eleve_list', 'nom': 'Gestion des Élèves'},
        {'code': 'professeur_list', 'nom': 'Gestion des Professeurs'},
        {'code': 'classe_list', 'nom': 'Gestion des Classes'},
        {'code': 'matiere_list', 'nom': 'Gestion des Matières'},
        {'code': 'attribution_list', 'nom': 'Attributions'},
        {'code': 'emploi_temps', 'nom': 'Emploi du Temps'},
        {'code': 'evaluation_list', 'nom': 'Évaluations'},
        {'code': 'saisie_notes', 'nom': 'Saisie des Notes'},
        {'code': 'presence_list', 'nom': 'Gestion des Présences'},
        {'code': 'paiement_list', 'nom': 'Gestion des Paiements'},
        {'code': 'frais_scolarite', 'nom': 'Frais de Scolarité'},
        {'code': 'bulletin_list', 'nom': 'Bulletins'},
        {'code': 'rapport_academique', 'nom': 'Rapports Académiques'},
        {'code': 'personnel_list', 'nom': 'Gestion du Personnel'},
        {'code': 'salaire_list', 'nom': 'Gestion des Salaires'},
        {'code': 'user_list', 'nom': 'Gestion des Utilisateurs'},
    ]
    
    # Construire service_data pour le template
    from authentification.models import Service, Module
    services = Service.objects.prefetch_related('modules').all()
    
    service_data = []
    for service in services:
        modules_list = []
        for module in service.modules.filter(est_actif=True):
            perm = permissions_existantes.get(module.code)
            
            # Logique des permissions:
            # - Si superadmin/direction: accès par défaut à tout, sauf si custom désactivé
            # - Sinon: accès uniquement si permission custom active
            if is_superadmin_or_direction:
                # Superadmin/Direction: accès par défaut, sauf si explicitement désactivé
                if module.code in custom_disabled_modules:
                    has_perm = False  # Explicitement désactivé
                    is_disabled = True
                elif module.code in custom_active_modules:
                    has_perm = True  # Custom permission active
                    is_disabled = False
                else:
                    has_perm = True  # Accès par défaut (pas de custom permission)
                    is_disabled = False
            else:
                # Autres rôles: accès uniquement via custom permission
                has_perm = perm is not None and perm.est_actif
                is_disabled = perm is None or (perm is not None and not perm.est_actif)
            
            # Construire la liste des actions
            actions = []
            if has_perm:
                if perm:
                    # Permissions personnalisées définies - utiliser la liste actions
                    actions = perm.actions if perm.actions else []
                elif is_superadmin_or_direction:
                    # Superadmin/Direction sans custom permission = full access
                    actions = ['read', 'create', 'update', 'delete', 'export']
            
            modules_list.append({
                'module': module,
                'has_permission': has_perm,
                'is_disabled': is_disabled,
                'is_custom': perm is not None,
                'actions': actions
            })
        
        if modules_list:
            service_data.append({
                'service': service,
                'modules': modules_list
            })
    
    return render(request, 'authentification/user_permissions_detail.html', {
        'target_user': utilisateur,
        'service_data': service_data,
        'permissions_existantes': permissions_existantes
    })


@login_required
def user_permission_toggle(request, user_pk, module_code):
    if not request.user.is_superadmin:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier les permissions.")
        return redirect('authentification:user_list')
    
    utilisateur = get_object_or_404(Utilisateur, pk=user_pk)
    from .models import Module
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            module = Module.objects.get(code=module_code)
        except Module.DoesNotExist:
            messages.error(request, f"Module {module_code} introuvable.")
            return redirect('authentification:user_permissions_detail', pk=user_pk)
        
        if action == 'toggle_module':
            # Activer/désactiver l'accès à un module
            perm, created = PermissionPersonnalisee.objects.get_or_create(
                utilisateur=utilisateur,
                module=module,
                defaults={'actions': ['read'], 'est_actif': True, 'niveau': 'utilisateur'}
            )
            if not created:
                perm.est_actif = not perm.est_actif
                perm.save()
            
            status = 'activé' if perm.est_actif else 'désactivé'
            messages.success(request, f"Accès au module {module.nom} {status} pour {utilisateur.get_full_name()}.")
        
        elif action == 'update_actions':
            # Mettre à jour les actions (lecture, création, modification, suppression)
            perm, created = PermissionPersonnalisee.objects.get_or_create(
                utilisateur=utilisateur,
                module=module,
                defaults={'est_actif': True, 'niveau': 'utilisateur'}
            )
            
            actions = request.POST.getlist('actions')
            perm.actions = actions if actions else ['read']
            perm.save()
            
            messages.success(request, f"Permissions du module {module.nom} mises à jour pour {utilisateur.get_full_name()}.")
    
    return redirect('authentification:user_permissions_detail', pk=user_pk)


@login_required
def user_reset_password(request, pk):
    if not request.user.is_superadmin:
        messages.error(request, "Vous n'avez pas l'autorisation de réinitialiser les mots de passe.")
        return redirect('authentification:user_list')
    
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            utilisateur.set_password(new_password)
            utilisateur.save(update_fields=['password'])
            log_audit(request.user, 'password_reset', utilisateur, f"Réinitialisation du mot de passe de {utilisateur.username}")
            messages.success(request, f'Mot de passe réinitialisé pour {utilisateur.get_full_name()}.')
        else:
            messages.error(request, 'Veuillez entrer un nouveau mot de passe.')
        return redirect('authentification:user_list')
    
    return redirect('authentification:user_list')


@login_required
def conversation_delete(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if not conversation.participants.filter(id=request.user.id).exists():
        messages.error(request, "Vous n'avez pas accès à cette conversation.")
        return redirect('authentification:message_list')
    
    is_admin = request.user.is_superadmin or request.user.role == Utilisateur.Role.DIRECTION
    
    if conversation.is_groupe:
        if not is_admin:
            messages.error(request, "Seuls l'administrateur et le directeur peuvent supprimer les groupes.")
            return redirect('authentification:message_conversation', conversation_id=conversation_id)
        
        conversation.delete()
        messages.success(request, "Groupe supprimé avec succès.")
    else:
        conversation.delete()
        messages.success(request, "Conversation supprimée.")
    
    return redirect('authentification:message_list')


@login_required
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    
    is_admin = request.user.is_superadmin or request.user.role == Utilisateur.Role.DIRECTION
    
    if not is_admin:
        if message.auteur != request.user and message.destinataire != request.user:
            messages.error(request, "Vous ne pouvez pas supprimer ce message.")
            return redirect('authentification:message_list')
    
    conversation_id = message.conversation_id if message.conversation else None
    message.delete()
    messages.success(request, "Message supprimé.")
    
    if conversation_id:
        return redirect('authentification:message_conversation', conversation_id=conversation_id)
    return redirect('authentification:message_list')


@login_required
def permissions_utilisateur(request):
    if not request.user.has_module_permission('permissions_utilisateur', 'read'):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    from .models import PermissionPersonnalisee, Service, Module
    services = Service.objects.filter(est_actif=True).order_by('ordre')
    modules = Module.objects.filter(est_actif=True).order_by('service__ordre', 'ordre')
    all_users = Utilisateur.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    utilisateur_id = request.GET.get('utilisateur')
    # Convertir en int pour comparaison
    utilisateur_id_int = int(utilisateur_id) if utilisateur_id and utilisateur_id.isdigit() else None
    
    # Récupérer toutes les permissions personnalisées actives
    perms_qs = PermissionPersonnalisee.objects.select_related(
        'utilisateur', 'module', 'module__service'
    ).filter(est_actif=True).order_by('utilisateur__first_name', 'module__nom')
    
    if utilisateur_id_int:
        perms_qs = perms_qs.filter(utilisateur_id=utilisateur_id_int)
    
    return render(request, 'authentification/permission_utilisateur_list.html', {
        'services': services,
        'modules': modules,
        'permissions': perms_qs,
        'all_users': all_users,
        'utilisateur_id': utilisateur_id_int,
        'utilisateur_id_str': str(utilisateur_id_int) if utilisateur_id_int else '',
    })


@login_required
def demandes_list(request):
    if not request.user.has_module_permission('demandes', 'read'):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    utilisateurs_en_attente = Utilisateur.objects.filter(is_active=False, is_approved=False).order_by('-date_joined')
    from .models import DemandeApprobation
    demandes = DemandeApprobation.objects.filter(statut='en_attente').order_by('-date_creation')
    demandes_traitees = DemandeApprobation.objects.exclude(statut='en_attente').order_by('-date_creation')[:50]
    return render(request, 'authentification/demande_list.html', {
        'demandes': demandes,
        'demandes_traitees': demandes_traitees,
    })


@login_required
def demande_detail(request, pk):
    from .models import DemandeApprobation
    demande = get_object_or_404(DemandeApprobation, pk=pk)
    return render(request, 'authentification/demande_detail.html', {'demande': demande})


@login_required
def demande_approuver(request, pk):
    from .models import DemandeApprobation
    if not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès refusé.")
        return redirect('authentification:demandes_list')
    demande = get_object_or_404(DemandeApprobation, pk=pk)
    if request.method == 'POST' or request.GET.get('confirm') == '1':
        demande.statut = 'approuve'
        demande.approbateur = request.user
        demande.save()
        messages.success(request, "Demande approuvée avec succès.")
        return redirect('authentification:demandes_list')
    return render(request, 'authentification/demande_detail.html', {'demande': demande, 'action': 'approuver'})


@login_required
def demande_rejeter(request, pk):
    from .models import DemandeApprobation
    if not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès refusé.")
        return redirect('authentification:demandes_list')
    demande = get_object_or_404(DemandeApprobation, pk=pk)
    if request.method == 'POST' or request.GET.get('confirm') == '1':
        demande.statut = 'rejete'
        demande.approbateur = request.user
        motif = request.POST.get('motif', '')
        if motif:
            demande.motif = motif
        demande.save()
        messages.success(request, "Demande rejetée.")
        return redirect('authentification:demandes_list')
    return render(request, 'authentification/demande_detail.html', {'demande': demande, 'action': 'rejeter'})


@login_required
def permission_utilisateur_create(request):
    from .models import PermissionPersonnalisee, Module
    from .forms import PermissionPersonnaliseeForm
    if not request.user.has_module_permission('permissions_utilisateur', 'write'):
        messages.error(request, "Accès refusé.")
        return redirect('authentification:permissions_utilisateur')
    if request.method == 'POST':
        form = PermissionPersonnaliseeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Permission créée avec succès.")
            return redirect('authentification:permissions_utilisateur')
    else:
        form = PermissionPersonnaliseeForm()
    return render(request, 'authentification/permission_utilisateur_form.html', {'form': form})


@login_required
def permission_utilisateur_edit(request, pk):
    from .models import PermissionPersonnalisee
    from .forms import PermissionPersonnaliseeForm
    if not request.user.has_module_permission('permissions_utilisateur', 'write'):
        messages.error(request, "Accès refusé.")
        return redirect('authentification:permissions_utilisateur')
    perm = get_object_or_404(PermissionPersonnalisee, pk=pk)
    if request.method == 'POST':
        form = PermissionPersonnaliseeForm(request.POST, instance=perm)
        if form.is_valid():
            form.save()
            messages.success(request, "Permission modifiée avec succès.")
            return redirect('authentification:permissions_utilisateur')
    else:
        form = PermissionPersonnaliseeForm(instance=perm)
    return render(request, 'authentification/permission_utilisateur_form.html', {'form': form, 'permission': perm})


@login_required
def permission_utilisateur_delete(request, pk):
    from .models import PermissionPersonnalisee
    if not request.user.has_module_permission('permissions_utilisateur', 'delete'):
        messages.error(request, "Accès refusé.")
        return redirect('authentification:permissions_utilisateur')
    perm = get_object_or_404(PermissionPersonnalisee, pk=pk)
    if request.method == 'POST':
        perm.delete()
        messages.success(request, "Permission supprimée avec succès.")
        return redirect('authentification:permissions_utilisateur')
    return render(request, 'authentification/permission_utilisateur_form.html', {'permission': perm, 'confirm_delete': True})


@login_required
def audit_log(request):
    """Vue pour le Journal d'Audit - Affiche les logs de toutes les actions"""
    from django.core.paginator import Paginator
    from .models import JournalAudit
    
    # Vérifier les permissions
    if not request.user.is_superuser and not request.user.est_direction():
        messages.error(request, "Accès refusé. Réservé aux administrateurs.")
        return redirect('dashboard')
    
    # Récupérer tous les logs avec filtres optionnels
    logs = JournalAudit.objects.all().select_related('utilisateur')
    
    # Filtres
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('utilisateur', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    search = request.GET.get('search', '')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    if user_filter:
        logs = logs.filter(utilisateur__username__icontains=user_filter)
    if date_debut:
        logs = logs.filter(created_at__date__gte=date_debut)
    if date_fin:
        logs = logs.filter(created_at__date__lte=date_fin)
    if search:
        logs = logs.filter(
            models.Q(object_repr__icontains=search) |
            models.Q(details__icontains=search) |
            models.Q(model__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': JournalAudit.objects.count(),
        'today': JournalAudit.objects.filter(created_at__date=timezone.now().date()).count(),
        'create': JournalAudit.objects.filter(action='create').count(),
        'update': JournalAudit.objects.filter(action='update').count(),
        'delete': JournalAudit.objects.filter(action='delete').count(),
        'login': JournalAudit.objects.filter(action='login').count(),
    }
    
    # Liste des actions pour le filtre
    actions = JournalAudit.Action.choices
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'actions': actions,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'search': search,
    }
    return render(request, 'authentification/audit_log.html', context)
