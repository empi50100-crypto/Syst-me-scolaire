from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login, logout, authenticate

from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib import messages

from django.views import View

from django.utils.decorators import method_decorator

from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt

from datetime import datetime

import pyotp

import qrcode

import io

import base64

from .models import User, log_audit, Notification, Message, DemandeApprobation, LoginAttempt, PermissionModification, Permission, Module, PermissionUtilisateur

from .forms import UserRegistrationForm, UserCreationForm, UserChangeForm


def redirect_to_users(request):
    return redirect('accounts:user_list')


def is_direction_or_superadmin(user):

    return user.is_authenticated and (user.is_direction() or user.is_superadmin())


def is_direction_or_comptable(user):

    return user.is_authenticated and (user.is_direction() or user.is_comptable() or user.is_superadmin())


class LoginView(View):

    template_name = 'accounts/login.html'

    two_factor_template = 'accounts/two_factor_login.html'

    
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

        
        from django.utils import timezone

        attempt_obj = LoginAttempt.objects.filter(username=username).first()

        
        if attempt_obj and attempt_obj.locked_until and attempt_obj.locked_until > timezone.now():

            remaining = int((attempt_obj.locked_until - timezone.now()).total_seconds() / 60) + 1

            messages.error(request, f'Compte temporairement bloqué. Réessayez dans {remaining} minute(s).')

            return render(request, self.template_name)

        
        user = authenticate(request, username=username, password=password)

        
        if user is not None:

            LoginAttempt.reset_attempts(username)

            
            if not user.is_approved and not user.is_superuser and user.role != User.Role.DIRECTION:

                messages.error(request, 'Votre compte est en attente de validation par l\'administrateur.')

                return render(request, self.template_name)

            
            if user.is_2fa_enabled and user.totp_secret:

                request.session['2fa_user_id'] = user.id

                request.session['2fa_method'] = 'totp'

                return render(request, self.two_factor_template)

            
            login(request, user)

            log_audit(user, 'login', 'User', user, 'Connexion réussie', request)

            messages.success(request, f'Bienvenue, {user.get_full_name() or user.username}!')

            next_url = request.GET.get('next', 'dashboard')

            return redirect(next_url)

        else:

            ip = self.get_client_ip(request)

            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

            
            attempt = LoginAttempt.record_failure(username, ip, user_agent)

            
            from django.utils import timezone

            if attempt.locked_until and attempt.locked_until > timezone.now():

                remaining = int((attempt.locked_until - timezone.now()).total_seconds() / 60) + 1

                messages.error(request, f'Compte temporairement bloqué. Réessayez dans {remaining} minute(s).')

            else:

                if attempt.attempts >= 5:

                    messages.error(request, 'Trop de tentatives échouées. Veuillez attendre ou utiliser la récupération d\'identifiant.')

                else:

                    messages.error(request, f'Nom d\'utilisateur ou mot de passe incorrect. ({5 - attempt.attempts} tentatives restantes)')

            
            return render(request, self.template_name)

    
    def verify_2fa(self, request):

        user_id = request.session.get('2fa_user_id')

        user = get_object_or_404(User, pk=user_id)

        token = request.POST.get('token', '').strip()

        
        if user.verify_totp(token):

            del request.session['2fa_user_id']

            del request.session['2fa_method']

            login(request, user)

            log_audit(user, 'login', 'User', user, 'Connexion 2FA réussie', request)

            messages.success(request, f'Bienvenue, {user.get_full_name() or user.username}!')

            next_url = request.GET.get('next', 'dashboard')

            return redirect(next_url)

        
        messages.error(request, 'Code invalide. Veuillez réessayer.')

        return render(request, self.two_factor_template)

    
    @staticmethod

    def get_client_ip(request):

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:

            ip = x_forwarded_for.split(',')[0]

        else:

            ip = request.META.get('REMOTE_ADDR')

        return ip


class TwoFactorSetupView(View):

    template_name = 'accounts/two_factor_setup.html'

    
    @method_decorator(login_required)

    def get(self, request):

        user = request.user

        if not user.totp_secret:

            user.generate_totp_secret()

            user.save()

        
        totp_uri = user.get_totp_uri()

        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)

        qr.add_data(totp_uri)

        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        
        buffer = io.BytesIO()

        img.save(buffer, format='PNG')

        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        
        if not user.backup_codes:

            backup_codes = user.generate_backup_codes()

        else:

            backup_codes = user.backup_codes

        
        return render(request, self.template_name, {

            'qr_code': qr_code_base64,

            'totp_uri': totp_uri,

            'backup_codes': backup_codes,

            'is_2fa_enabled': user.is_2fa_enabled,

        })

    
    @method_decorator(login_required)

    def post(self, request):

        user = request.user

        action = request.POST.get('action')

        
        if action == 'enable':

            token = request.POST.get('token', '').strip()

            if user.verify_totp(token):

                user.is_2fa_enabled = True

                user.save()

                messages.success(request, 'Authentification à deux facteurs activée avec succès!')

                log_audit(user, 'update', 'User', user, '2FA activé', request)

            else:

                messages.error(request, 'Code invalide. Veuillez réessayer.')

                return redirect('accounts:two_factor_setup')

        
        elif action == 'disable':

            token = request.POST.get('token', '').strip()

            if user.verify_totp(token):

                user.is_2fa_enabled = False

                user.save()

                messages.success(request, 'Authentification à deux facteurs désactivée.')

                log_audit(user, 'update', 'User', user, '2FA désactivé', request)

            else:

                messages.error(request, 'Code invalide. Veuillez réessayer.')

                return redirect('accounts:two_factor_setup')

        
        elif action == 'regenerate_codes':

            token = request.POST.get('token', '').strip()

            if user.verify_totp(token):

                backup_codes = user.generate_backup_codes()

                user.save()

                messages.success(request, 'Codes de secours régénénés. Les anciens codes sont invalides.')

                log_audit(user, 'update', 'User', user, 'Codes 2FA régénérés', request)

                return redirect('accounts:two_factor_setup')

            else:

                messages.error(request, 'Code invalide. Veuillez réessayer.')

                return redirect('accounts:two_factor_setup')

        
        return redirect('accounts:profile')


class RegisterView(View):

    template_name = 'accounts/register.html'

    
    def get(self, request):

        if request.user.is_authenticated:

            return redirect('dashboard')

        form = UserRegistrationForm()

        return render(request, self.template_name, {'form': form})

    
    def post(self, request):

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            
            Notification.creer_notification(

                destinataire=user,

                type_notification=Notification.TypeNotification.COMPTE_ATTENTE,

                titre='Compte créé',

                message='Votre compte a été créé avec succès. Il sera activé après validation par l\'administrateur.'

            )

            
            admins = User.objects.filter(role__in=[User.Role.DIRECTION, User.Role.SUPERADMIN], is_active=True)

            for admin in admins:

                Notification.creer_notification(

                    destinataire=admin,

                    type_notification=Notification.TypeNotification.COMPTE_ATTENTE,

                    titre='Nouveau compte en attente',

                    message=f'{user.get_full_name()} a créé un compte et attend validation.',

                    lien='/accounts/users/'

                )

            
            messages.success(request, 'Votre compte a été créé avec succès. Il sera activé après validation par l\'administrateur.')

            return redirect('accounts:login')

        return render(request, self.template_name, {'form': form})


class LogoutView(View):

    def get(self, request):

        logout(request)

        messages.info(request, 'Vous avez été déconnecté.')

        return redirect('accounts:login')

    
    def post(self, request):

        logout(request)

        messages.info(request, 'Vous avez été déconnecté.')

        return redirect('accounts:login')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
@login_required
def locked_accounts(request):
    if not request.user.has_module_permission("user_list", "read"):

        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")

        return redirect('dashboard')

    from django.utils import timezone
    
    locked = LoginAttempt.objects.filter(
        locked_until__isnull=False,
        locked_until__gt=timezone.now()
    ).order_by('locked_until')
    
    return render(request, 'accounts/locked_accounts.html', {
        'locked_accounts': locked,
    })


@login_required
@login_required
def permission_check_view(request):
    if not request.user.has_module_permission('user_list', 'write'):

        messages.error(request, "Vous n'avez pas l'autorisation de créer des utilisateurs.")

        return redirect('accounts:user_list')

    
    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(request, f'Utilisateur {user.get_full_name()} créé avec succès.')

            return redirect('accounts:user_list')

    else:

        form = UserCreationForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Créer'})



@login_required
@login_required
def permission_check_view(request):
    if not request.user.has_module_permission('user_list', 'update'):

        messages.error(request, "Vous n'avez pas l'autorisation de modifier des utilisateurs.")

        return redirect('accounts:user_list')

    
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':

        form = UserChangeForm(request.POST, instance=user)

        if form.is_valid():

            form.save()

            messages.success(request, 'Utilisateur modifié avec succès.')

            return redirect('accounts:user_list')

    else:

        form = UserChangeForm(instance=user)

    return render(request, 'accounts/user_form.html', {'form': form, 'user': user, 'action': 'Modifier'})



@login_required
@login_required
def permission_check_view(request):
    if not request.user.has_module_permission('user_list', 'delete'):

        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des utilisateurs.")

        return redirect('accounts:user_list')

    
    user = get_object_or_404(User, pk=pk)

    if request.user == user:

        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')

        return redirect('accounts:user_list')

    
    if request.method == 'POST':

        user.delete()

        messages.success(request, 'Utilisateur supprimé.')

        return redirect('accounts:user_list')

    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})



@login_required
@login_required
def permission_check_view(request):
    if not request.user.has_module_permission('user_list', 'update'):

        messages.error(request, "Vous n'avez pas l'autorisation de modifier des utilisateurs.")

        return redirect('accounts:user_list')

    
    user = get_object_or_404(User, pk=pk)

    if request.user == user:

        messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')

        return redirect('accounts:user_list')

    
    user.is_active = not user.is_active

    user.save()

    status = "activé" if user.is_active else "désactivé"

    messages.success(request, f'Compte {status}.')

    return redirect('accounts:user_list')



@login_required
@login_required
def permission_check_view(request):
    if not request.user.has_module_permission('user_list', 'update'):

        messages.error(request, "Vous n'avez pas l'autorisation d'approuver des utilisateurs.")

        return redirect('accounts:user_list')

    
    user = get_object_or_404(User, pk=pk)

    user.is_approved = True

    user.save()

    
    Notification.creer_notification(

        destinataire=user,

        type_notification=Notification.TypeNotification.COMPTE_APPROUVE,

        titre='Compte approuvé',

        message='Votre compte a été approuvé par l\'administrateur. Vous pouvez maintenant vous connecter.'

    )

    
    messages.success(request, f'Compte de {user.get_full_name()} approuvé.')

    return redirect('accounts:user_list')



@login_required
@login_required
def permission_check_view(request):
    if not request.user.has_module_permission('user_list', 'update'):

        messages.error(request, "Vous n'avez pas l'autorisation de réinitialiser les mots de passe.")

        return redirect('accounts:user_list')

    
    if request.method == 'POST':

        user = get_object_or_404(User, pk=pk)

        new_password = request.POST.get('new_password')

        if new_password:

            user.set_password(new_password)

            user.save()

            messages.success(request, f'Mot de passe de {user.get_full_name()} réinitialisé.')

        else:

            messages.error(request, 'Veuillez entrer un nouveau mot de passe.')

    return redirect('accounts:user_list')



@login_required
@login_required
def eleve_list_view(request):
    if not request.user.has_module_permission("eleve_list", "read"):

        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")

        return redirect('dashboard')

    
    user = get_object_or_404(User, pk=pk)

    messages.info(request, f'Mot de passe de {user.get_full_name()}: {{ user.username }} (mot de passe non stocké)')

    return redirect('accounts:user_list')



@login_required
@login_required
def user_list(request):
    if not request.user.has_module_permission("user_list", "read"):

        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")

        return redirect('dashboard')

    
    users = User.objects.order_by('-date_joined')

    
    if request.user.is_superadmin():

        users = users.exclude(role=User.Role.SUPERADMIN)

    elif request.user.is_direction():

        users = users.exclude(role=User.Role.SUPERADMIN)

    
    total_users = users.count()

    approved_users = users.filter(is_approved=True).count()

    pending_users = users.filter(is_approved=False).count()

    inactive_users = users.filter(is_active=False).count()

    return render(request, 'accounts/user_list.html', {

        'users': users,

        'total_users': total_users,

        'approved_users': approved_users,

        'pending_users': pending_users,

        'inactive_users': inactive_users,

    })


@login_required
def unlock_account(request, username):
    LoginAttempt.unlock(username)

    messages.success(request, f'Compte "{username}" déverrouillé.')

    return redirect('accounts:locked_accounts')



@login_required
@login_required
def view_func(request):
    filter_type = request.GET.get('filter', 'all')

    
    if filter_type == 'unread':

        notifications = request.user.notifications.filter(est_lu=False)

    elif filter_type == 'read':

        notifications = request.user.notifications.filter(est_lu=True)

    else:

        notifications = request.user.notifications.all()

    
    return render(request, 'accounts/notification_list.html', {

        'notifications': notifications[:50],

        'filter_type': filter_type

    })



@login_required
@login_required
def view_func(request):
    request.user.notifications.filter(est_lu=False).update(est_lu=True)

    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')

    return redirect('accounts:notification_list')



@login_required
@login_required
def view_func(request, pk):
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)

    if not notification.est_lu:

        notification.est_lu = True

        notification.save()

    
    if notification.lien:

        return redirect(notification.lien)

    
    return render(request, 'accounts/notification_detail.html', {'notification': notification})



@login_required
@login_required
def view_func(request):
    count = request.user.notifications.filter(est_lu=False).count()

    return {'notification_non_lues': count}



@login_required
@login_required
def view_func(request):
    filter_type = request.GET.get('filter', 'all')

    
    if filter_type == 'unread':

        messages_recus = request.user.messages_recus.filter(est_lu=False, type_message=Message.TypeMessage.INDIVIDUEL)

    elif filter_type == 'read':

        messages_recus = request.user.messages_recus.filter(est_lu=True, type_message=Message.TypeMessage.INDIVIDUEL)

    else:

        messages_recus = request.user.messages_recus.filter(type_message=Message.TypeMessage.INDIVIDUEL)

    
    messages_envoyes = request.user.messages_envoyes.filter(type_message=Message.TypeMessage.INDIVIDUEL).order_by('-date_envoi')[:50]

    messages_services = Message.objects.filter(service=request.user.role).order_by('-date_envoi')[:50]

    
    return render(request, 'accounts/message_list.html', {

        'messages_recus': messages_recus[:50],

        'messages_envoyes': messages_envoyes,

        'messages_groupes': messages_services,

        'filter_type': filter_type

    })



@login_required
@login_required
def view_func(request):
    request.user.messages_recus.filter(est_lu=False).update(est_lu=True)

    messages.success(request, 'Tous les messages ont été marqués comme lus.')

    return redirect('accounts:message_list')



@login_required
@login_required
def view_func(request):
    reply_to = request.GET.get('reply_to')

    reply_sujet = request.GET.get('sujet', '')

    
    if request.method == 'POST':

        destinataire_id = request.POST.get('destinataire')

        sujet = request.POST.get('sujet')

        contenu = request.POST.get('contenu')

        type_message = request.POST.get('type_message', 'individuel')

        
        if type_message == 'individuel' and destinataire_id:

            Message.objects.create(

                auteur=request.user,

                type_message=Message.TypeMessage.INDIVIDUEL,

                destinataire_id=destinataire_id,

                sujet=sujet,

                contenu=contenu

            )

            destinataire = User.objects.get(pk=destinataire_id)

            messages.success(request, 'Message envoyé avec succès.')

        elif type_message == 'service':

            service = request.POST.get('service')

            if service:

                Message.objects.create(

                    auteur=request.user,

                    type_message=Message.TypeMessage.SERVICE,

                    service=service,

                    sujet=sujet,

                    contenu=contenu

                )

                messages.success(request, f'Message envoyé au service.')

            else:

                messages.error(request, 'Veuillez sélectionner un service.')

        else:

            messages.error(request, 'Veuillez sélectionner un destinataire.')

        
        return redirect('accounts:message_list')

    
    utilisateurs = User.objects.filter(is_active=True, is_approved=True).exclude(pk=request.user.pk)

    destinataire_preselection = None

    if reply_to:

        destinataire_preselection = User.objects.filter(pk=reply_to).first()

    
    return render(request, 'accounts/message_form.html', {

        'utilisateurs': utilisateurs,

        'destinataire_preselection': destinataire_preselection,

        'reply_sujet': reply_sujet

    })

    
    utilisateurs = User.objects.filter(is_active=True, is_approved=True).exclude(pk=request.user.pk)

    return render(request, 'accounts/message_form.html', {'utilisateurs': utilisateurs})



@login_required
@login_required
def view_func(request, pk):
    message = Message.objects.filter(pk=pk).first()

    if not message:

        messages.error(request, 'Message non trouvé.')

        return redirect('accounts:message_list')

    
    if message.destinataire == request.user and not message.est_lu:

        message.est_lu = True

        message.save()

    
    return render(request, 'accounts/message_detail.html', {'message': message})



@login_required
@login_required
def view_func(request):
    from django.db.models import Max, Q

    from accounts.models import Message

    
    user = request.user

    sent = Message.objects.filter(auteur=user, type_message=Message.TypeMessage.INDIVIDUEL).values('destinataire').annotate(last_msg=Max('date_envoi'))

    received = Message.objects.filter(destinataire=user, type_message=Message.TypeMessage.INDIVIDUEL).values('auteur').annotate(last_msg=Max('date_envoi'))

    
    user_ids = set()

    for item in list(sent) + list(received):

        if item.get('destinataire'):

            user_ids.add(item['destinataire'])

        if item.get('auteur'):

            user_ids.add(item['auteur'])

    user_ids.discard(None)

    
    conversations = []

    for other_user in User.objects.filter(pk__in=user_ids).order_by('first_name', 'username'):

        last_msg = Message.objects.filter(

            Q(auteur=user, destinataire=other_user) | Q(auteur=other_user, destinataire=user),

            type_message=Message.TypeMessage.INDIVIDUEL

        ).order_by('-date_envoi').first()

        
        unread_count = Message.objects.filter(

            destinataire=user,

            auteur=other_user,

            est_lu=False,

            type_message=Message.TypeMessage.INDIVIDUEL

        ).count()

        
        conversations.append({

            'autre_user': other_user,

            'last_message': last_msg,

            'unread_count': unread_count

        })

    
    return render(request, 'accounts/chat_inbox.html', {'conversations': conversations})



@login_required
@login_required
def view_func(request, pk):
    utilisateurs = User.objects.filter(is_active=True, is_approved=True).exclude(pk=request.user.pk).order_by('first_name', 'username')

    return render(request, 'accounts/chat_new.html', {'utilisateurs': utilisateurs})



@login_required
@login_required
def view_func(request, pk):
    autre_user = get_object_or_404(User, pk=user_id)

    messages = Message.get_conversation(request.user, autre_user)

    
    messages.filter(destinataire=request.user, est_lu=False).update(est_lu=True)

    
    if request.method == 'POST':

        contenu = request.POST.get('contenu', '').strip()

        if contenu:

            Message.objects.create(

                auteur=request.user,

                type_message=Message.TypeMessage.INDIVIDUEL,

                destinataire=autre_user,

                contenu=contenu

            )

            return redirect('chat_conversation', user_id=user_id)

    
    return render(request, 'accounts/chat_conversation.html', {

        'autre_user': autre_user,

        'messages': messages,

        'hide_messages': True

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def demande_list(request):
    demandes = DemandeApprobation.objects.filter(statut=DemandeApprobation.Statut.EN_ATTENTE).order_by('-date_creation')

    demandes_traitees = DemandeApprobation.objects.exclude(statut=DemandeApprobation.Statut.EN_ATTENTE).order_by('-date_traitement')[:50]

    log_audit(request.user, 'view', 'DemandeApprobation', None, 'Liste des demandes d\'approbation', request)

    return render(request, 'accounts/demande_list.html', {

        'demandes': demandes,

        'demandes_traitees': demandes_traitees

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def demande_detail(request, pk):
    demande = get_object_or_404(DemandeApprobation, pk=pk)

    return render(request, 'accounts/demande_detail.html', {'demande': demande})


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def demande_approuver(request, pk):
    demande = get_object_or_404(DemandeApprobation, pk=pk)

    
    if demande.statut != DemandeApprobation.Statut.EN_ATTENTE:

        messages.error(request, 'Cette demande a déjà été traitée.')

        return redirect('accounts:demande_list')

    
    observations = request.POST.get('observations', '')

    
    from eleves.models import Eleve

    from finances.models import EcoleCompte, Salaire

    from accounts.models import log_audit

    from django.utils import timezone

    
    objet_execute = False

    
    if demande.type_objet == DemandeApprobation.TypeObjet.ELEVE:

        if demande.type_action == DemandeApprobation.TypeAction.CREATION:

            from eleves.forms import EleveForm

            from django.utils import timezone

            now = timezone.now()

            parts = demande.details_apos.split('\n')

            eleve_data = {}

            for line in parts:

                if ':' in line:

                    key, value = line.split(':', 1)

                    key = key.strip().lower().replace(' ', '_')

                    value = value.strip()

                    if key in ['nom', 'prenom', 'date_de_naissance', 'lieu_de_naissance', 'sexe', 'adresse', 'téléphone_parent', 'email_parent']:

                        eleve_data[key] = value

            
            date_naissance = now.date()

            if 'Date de naissance:' in demande.details_apos:

                try:

                    date_naissance = datetime.strptime(demande.details_apos.split('Date de naissance:')[1].split('\n')[0].strip(), '%Y-%m-%d').date()

                except:

                    try:

                        date_naissance = datetime.strptime(demande.details_apos.split('Date de naissance:')[1].split('\n')[0].strip(), '%d/%m/%Y').date()

                    except:

                        pass

            
            telephone_parent = ''

            if 'Téléphone parent:' in demande.details_apos:

                telephone_parent = demande.details_apos.split('Téléphone parent:')[1].split('\n')[0].strip()

            
            email_parent = ''

            if 'Email parent:' in demande.details_apos:

                email_parent = demande.details_apos.split('Email parent:')[1].split('\n')[0].strip()

            
            statut = 'actif'

            if 'Statut:' in demande.details_apos:

                statut_str = demande.details_apos.split('Statut:')[1].split('\n')[0].strip().lower()

                if 'inactif' in statut_str:

                    statut = 'inactif'

                elif 'supprim' in statut_str:

                    statut = 'supprime'

            
            eleve = Eleve(

                nom=demande.details_apos.split('Nom:')[1].split('\n')[0].strip() if 'Nom:' in demande.details_apos else 'Inconnu',

                prenom=demande.details_apos.split('Prénom:')[1].split('\n')[0].strip() if 'Prénom:' in demande.details_apos else 'Inconnu',

                date_naissance=date_naissance,

                lieu_naissance=demande.details_apos.split('Lieu de naissance:')[1].split('\n')[0].strip() if 'Lieu de naissance:' in demande.details_apos else 'Inconnu',

                sexe=demande.details_apos.split('Sexe:')[1].split('\n')[0].strip() if 'Sexe:' in demande.details_apos else 'M',

                adresse=demande.details_apos.split('Adresse:')[1].split('\n')[0].strip() if 'Adresse:' in demande.details_apos else '',

                telephone_parent=telephone_parent,

                email_parent=email_parent,

                statut=statut

            )

            eleve.save()

            demande.objet_id = eleve.pk

            objet_execute = True

            messages.success(request, f'Élève {eleve.nom_complet} créé avec succès.')

            log_audit(request.user, 'create', 'Eleve', eleve, 'Création approuvée par Direction', request)

            
        elif demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

            if demande.objet_id:

                eleve = Eleve.objects.filter(pk=demande.objet_id).first()

                if eleve:

                    details = demande.details_apos

                    if 'Nom:' in details:

                        eleve.nom = details.split('Nom:')[1].split('\n')[0].strip()

                    if 'Prénom:' in details:

                        eleve.prenom = details.split('Prénom:')[1].split('\n')[0].strip()

                    if 'Date de naissance:' in details:

                        try:

                            date_str = details.split('Date de naissance:')[1].split('\n')[0].strip()

                            try:

                                eleve.date_naissance = datetime.strptime(date_str, '%Y-%m-%d').date()

                            except:

                                eleve.date_naissance = datetime.strptime(date_str, '%d/%m/%Y').date()

                        except:

                            pass

                    if 'Lieu de naissance:' in details:

                        eleve.lieu_naissance = details.split('Lieu de naissance:')[1].split('\n')[0].strip()

                    if 'Sexe:' in details:

                        eleve.sexe = details.split('Sexe:')[1].split('\n')[0].strip()[0]

                    if 'Adresse:' in details:

                        eleve.adresse = details.split('Adresse:')[1].split('\n')[0].strip()

                    if 'Téléphone parent:' in details:

                        eleve.telephone_parent = details.split('Téléphone parent:')[1].split('\n')[0].strip()

                    if 'Email parent:' in details:

                        eleve.email_parent = details.split('Email parent:')[1].split('\n')[0].strip()

                    if 'Statut:' in details:

                        statut_str = details.split('Statut:')[1].split('\n')[0].strip().lower()

                        if 'inactif' in statut_str:

                            eleve.statut = 'inactif'

                        elif 'supprim' in statut_str:

                            eleve.statut = 'supprime'

                        else:

                            eleve.statut = 'actif'

                    eleve.save()

                    objet_execute = True

                    messages.success(request, f'Élève {eleve.nom_complet} modifié avec succès.')

                    log_audit(request.user, 'update', 'Eleve', eleve, 'Modification approuvée par Direction', request)

        
        elif demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                eleve = Eleve.objects.filter(pk=demande.objet_id).first()

                if eleve:

                    nom_eleve = eleve.nom_complet

                    eleve.statut = 'supprime'

                    eleve.save()

                    objet_execute = True

                    messages.success(request, f'Élève {nom_eleve} supprimé avec succès.')

                    log_audit(request.user, 'delete', 'Eleve', eleve, 'Suppression approuvée par Direction', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.SALAIRE:

        personnel_nom = demande.details.split('Personnel:')[1].split('\n')[0].strip() if 'Personnel:' in demande.details else ''

        mois_str = demande.details.split('Mois:')[1].split('\n')[0].strip() if 'Mois:' in demande.details else ''

        annee_str = demande.details.split(' ')[-1].strip() if 'annee' in demande.details.lower() else str(datetime.now().year)

        
        from finances.models import Personnel

        personnel = Personnel.objects.filter(nom__icontains=personnel_nom.split()[0] if personnel_nom else '').first()

        
        if personnel:

            mois_num = 1

            for i, m in enumerate(['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'], 1):

                if m.lower() in mois_str.lower():

                    mois_num = i

                    break

            
            annee = int(annee_str) if annee_str.isdigit() else datetime.now().year

            
            salaire_brut = 0

            retenues = 0

            if 'Salaire brut:' in demande.details:

                try:

                    salaire_brut = float(demande.details.split('Salaire brut:')[1].split('FCFA')[0].strip())

                except:

                    salaire_brut = float(personnel.salaire_mensuel or 0)

            if 'Retenues:' in demande.details:

                try:

                    retenues = float(demande.details.split('Retenues:')[1].split('FCFA')[0].strip())

                except:

                    retenues = 0

            
            est_paye = 'Payé: Oui' in demande.details

            
            salaire = Salaire.objects.create(

                personnel=personnel,

                mois=mois_num,

                annee=annee,

                salaire_brut=salaire_brut or float(personnel.salaire_mensuel or 0),

                retenues=retenues,

                salaire_net=(salaire_brut or float(personnel.salaire_mensuel or 0)) - retenues,

                est_paye=est_paye,

                date_versement=datetime.now().date() if est_paye else None

            )

            demande.objet_id = salaire.pk

            objet_execute = True

            messages.success(request, f'Salaire de {personnel} enregistré.')

            log_audit(request.user, 'create', 'Salaire', salaire, 'Paiement salaire approuvé', request)

    
    elif demande.type_objet in [DemandeApprobation.TypeObjet.ENCAISSEMENT, DemandeApprobation.TypeObjet.DECAISSEMENT]:

        type_operation = 'encaissement' if demande.type_objet == DemandeApprobation.TypeObjet.ENCAISSEMENT else 'decaissement'

        
        categorie = demande.details.split('Catégorie:')[1].split('\n')[0].strip() if 'Catégorie:' in demande.details else 'Autre'

        montant = 0

        if 'Montant:' in demande.details:

            try:

                montant = float(demande.details.split('Montant:')[1].split('FCFA')[0].strip())

            except:

                pass

        motif = demande.details.split('Motif:')[1].strip() if 'Motif:' in demande.details else ''

        beneficiaire = demande.details.split('Bénéficiaire:')[1].split('\n')[0].strip() if 'Bénéficiaire:' in demande.details else ''

        
        if montant > 0:

            operation = EcoleCompte.objects.create(

                date_operation=datetime.now().date(),

                type_operation=type_operation,

                categorie=categorie,

                montant=montant,

                motif=motif,

                beneficiaire=beneficiaire,

                personnel=demande.demandeur

            )

            demande.objet_id = operation.pk

            objet_execute = True

            messages.success(request, f'Opération de {type_operation} enregistrée.')

            log_audit(request.user, 'create', 'EcoleCompte', operation, f'{type_operation} approuvé', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.MATIERE:

        from academics.models import Matiere

        if demande.type_action == DemandeApprobation.TypeAction.CREATION:

            nom = demande.details.split('Nom:')[1].split('\n')[0].strip() if 'Nom:' in demande.details else 'Inconnu'

            code = demande.details.split('Code:')[1].split('\n')[0].strip() if 'Code:' in demande.details else ''

            coef = demande.details.split('Coefficient:')[1].split('\n')[0].strip() if 'Coefficient:' in demande.details else '1'

            
            matiere = Matiere.objects.create(

                nom=nom,

                code=code,

                coefficient=int(coef) if coef.isdigit() else 1

            )

            demande.objet_id = matiere.pk

            objet_execute = True

            messages.success(request, f'Matière {matiere.nom} créée avec succès.')

            log_audit(request.user, 'create', 'Matiere', matiere, 'Création approuvée', request)

            
        elif demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

            if demande.objet_id:

                matiere = Matiere.objects.filter(pk=demande.objet_id).first()

                if matiere:

                    details = demande.details_apos

                    if 'Nom:' in details:

                        matiere.nom = details.split('Nom:')[1].split('\n')[0].strip()

                    if 'Code:' in details:

                        matiere.code = details.split('Code:')[1].split('\n')[0].strip()

                    if 'Coefficient:' in details:

                        try:

                            matiere.coefficient = int(details.split('Coefficient:')[1].split('\n')[0].strip())

                        except:

                            pass

                    matiere.save()

                    objet_execute = True

                    messages.success(request, f'Matière {matiere.nom} modifiée.')

                    log_audit(request.user, 'update', 'Matiere', matiere, 'Modification approuvée', request)

                    
        elif demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                matiere = Matiere.objects.filter(pk=demande.objet_id).first()

                if matiere:

                    nom_matiere = str(matiere)

                    matiere.delete()

                    objet_execute = True

                    messages.success(request, f'Matière supprimée.')

                    log_audit(request.user, 'delete', 'Matiere', None, f'Suppression approuvée: {nom_matiere}', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.ATTRIBUTION:

        from academics.models import Enseignement, Classe, Matiere,Professeur as Prof

        if demande.type_action == DemandeApprobation.TypeAction.CREATION:

            classe_nom = demande.details.split('Classe:')[1].split('\n')[0].strip() if 'Classe:' in demande.details else ''

            matiere_nom = demande.details.split('Matière:')[1].split('\n')[0].strip() if 'Matière:' in demande.details else ''

            prof_nom = demande.details.split('Professeur:')[1].split('\n')[0].strip() if 'Professeur:' in demande.details else ''

            
            classe = Classe.objects.filter(nom__icontains=classe_nom.split()[0] if classe_nom else '').first()

            matiere = Matiere.objects.filter(nom__icontains=matiere_nom.split()[0] if matiere_nom else '').first()

            prof = Prof.objects.filter(nom__icontains=prof_nom.split()[0] if prof_nom else '').first()

            
            if classe and matiere and prof:

                ens = Enseignement.objects.create(

                    classe=classe,

                    matiere=matiere,

                    professeur=prof,

                    annee_scolaire=annee_active

                )

                demande.objet_id = ens.pk

                objet_execute = True

                messages.success(request, f'Attribution créée: {classe.nom} - {matiere.nom} - {prof}')

                log_audit(request.user, 'create', 'Enseignement', ens, 'Attribution créée', request)

                
        elif demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

            if demande.objet_id:

                ens = Enseignement.objects.filter(pk=demande.objet_id).first()

                if ens:

                    details = demande.details_apos

                    # Update logic here

                    ens.save()

                    objet_execute = True

                    messages.success(request, 'Attribution modifiée.')

                    log_audit(request.user, 'update', 'Enseignement', ens, 'Attribution modifiée', request)

                    
        elif demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                ens = Enseignement.objects.filter(pk=demande.objet_id).first()

                if ens:

                    ens.delete()

                    objet_execute = True

                    messages.success(request, 'Attribution supprimée.')

                    log_audit(request.user, 'delete', 'Enseignement', None, 'Attribution supprimée', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.CONTRAINTE:

        from academics.models import ContrainteHoraire

        if demande.type_action == DemandeApprobation.TypeAction.CREATION:

            details = demande.details_apos

            
            if 'Professeur:' in details:

                prof_nom = details.split('Professeur:')[1].split('\n')[0].strip()

            elif 'Demande de' in details:

                type_contrainte = details.split('Demande de')[1].split('\n')[0].strip()

            else:

                prof_nom = ''

            
            if 'Jour:' in details:

                jour = details.split('Jour:')[1].split('\n')[0].strip().lower()

            
            if 'Heure de debut:' in details:

                from datetime import datetime

                try:

                    h_debut = datetime.strptime(details.split('Heure de debut:')[1].split('\n')[0].strip(), '%H:%M').time()

                except:

                    h_debut = None

            else:

                h_debut = None

                
            if 'Heure de fin:' in details:

                try:

                    h_fin = datetime.strptime(details.split('Heure de fin:')[1].split('\n')[0].strip(), '%H:%M').time()

                except:

                    h_fin = None

            else:

                h_fin = None

            
            type_cont = 'autre'

            if 'Type:' in details:

                type_str = details.split('Type:')[1].split('\n')[0].strip().lower()

                for choice in ContrainteHoraire.TypeContrainte.choices:

                    if choice[1].lower() == type_str:

                        type_cont = choice[0]

                        break

            
            motif = ''

            if 'Motif:' in details:

                motif = details.split('Motif:')[1].split('\n')[0].strip()

            
            recurrent = 'Non'

            if 'Récurrent:' in details:

                recurrent = details.split('Récurrent:')[1].split('\n')[0].strip()

            
            date_fin = None

            if 'Date fin:' in details:

                date_str = details.split('Date fin:')[1].split('\n')[0].strip()

                if date_str != 'Non définie':

                    try:

                        date_fin = datetime.strptime(date_str, '%Y-%m-%d').date()

                    except:

                        pass

            
            from academics.models import Professeur

            prof = None

            if prof_nom and prof_nom != 'Non spécifié':

                parts = prof_nom.split()

                if len(parts) >= 2:

                    prof = Professeur.filter(nom__icontains=parts[-1], prenom__icontains=parts[0]).first()

            
            if prof and jour and h_debut and h_fin:

                contrainte = ContrainteHoraire.objects.create(

                    professeur=prof,

                    jour=jour,

                    heure_debut=h_debut,

                    heure_fin=h_fin,

                    type_contrainte=type_cont,

                    motif=motif,

                    est_recurrent='Oui' in recurrent,

                    date_fin=date_fin,

                    statut=ContrainteHoraire.Statut.APPROUVE,

                    demande_approuver=demande

                )

                demande.objet_id = contrainte.pk

                objet_execute = True

                messages.success(request, f'Contrainte créée: {prof} - {jour.capitalize()} {h_debut}-{h_fin}')

                log_audit(request.user, 'create', 'ContrainteHoraire', contrainte, 'Contrainte créée', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.CLASSE:

        from academics.models import Classe, Matiere, ClasseMatiere

        from eleves.models import Inscription, Eleve

        from finances.models import AnneeScolaire

        
        annee_active = AnneeScolaire.objects.filter(est_active=True).first()

        
        if demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

            if demande.objet_id:

                classe = Classe.objects.filter(pk=demande.objet_id).first()

                if classe:

                    details = demande.details_apos

                    
                    if 'Nom:' in details:

                        classe.nom = details.split('Nom:')[1].split('\n')[0].strip()

                    if 'Niveau:' in details:

                        niveau = details.split('Niveau:')[1].split('\n')[0].strip()

                        for choice in Classe.Niveau.choices:

                            if choice[1].lower() == niveau.lower():

                                classe.niveau = choice[0]

                                break

                        else:

                            classe.niveau = niveau

                    if 'Série:' in details:

                        serie = details.split('Série:')[1].split('\n')[0].strip()

                        for choice in Classe.Serie.choices:

                            if choice[1].lower() == serie.lower():

                                classe.serie = choice[0]

                                break

                        else:

                            classe.serie = serie

                    if 'Domaine:' in details:

                        classe.domaine = details.split('Domaine:')[1].split('\n')[0].strip()

                    classe.save()

                    
                    matieres_ajoutees = 0

                    if 'Matières:' in details:

                        matieres_section = details.split('Matières:')[1].split('\n')[0].strip()

                        if matieres_section and matieres_section != "Aucune":

                            matiere_names = [m.strip() for m in matieres_section.split(',')]

                            for matiere_name in matiere_names:

                                matiere_clean = matiere_name.split(' (coef:')[0].strip()

                                matiere = Matiere.objects.filter(nom__iexact=matiere_clean).first()

                                if not matiere:

                                    matiere = Matiere.objects.filter(nom__icontains=matiere_clean).first()

                                if matiere:

                                    cm, created = ClasseMatiere.objects.get_or_create(

                                        classe=classe,

                                        matiere=matiere,

                                        defaults={'coefficient': matiere.coefficient}

                                    )

                                    if created:

                                        matieres_ajoutees += 1

                    
                    eleves_ajoutes = 0

                    if 'Élèves:' in details and annee_active:

                        eleves_section = details.split('Élèves:')[1].split('\n')[0].strip()

                        if eleves_section and eleves_section != "Aucun":

                            eleve_names = [e.strip() for e in eleves_section.split(',')]

                            for eleve_nom in eleve_names:

                                parts = eleve_nom.strip().split()

                                if len(parts) >= 2:

                                    nom = parts[-1]

                                    prenom = parts[0]

                                    eleve = Eleve.objects.filter(

                                        nom__icontains=nom,

                                        prenom__icontains=prenom

                                    ).first()

                                    if not eleve:

                                        full_name_parts = eleve_nom.split()

                                        if len(full_name_parts) >= 2:

                                            eleve = Eleve.objects.filter(

                                                nom__icontains=full_name_parts[0],

                                                prenom__icontains=full_name_parts[-1]

                                            ).first()

                                    if eleve:

                                        ins, created = Inscription.objects.get_or_create(

                                            eleve=eleve,

                                            classe=classe,

                                            annee_scolaire=annee_active

                                        )

                                        if created:

                                            eleves_ajoutes += 1

                    
                    objet_execute = True

                    
                    parts_msg = []

                    if matieres_ajoutees > 0:

                        parts_msg.append(f"{matieres_ajoutees} matière(s)")

                    if eleves_ajoutes > 0:

                        parts_msg.append(f"{eleves_ajoutes} élève(s)")

                    
                    if parts_msg:

                        messages.success(request, f"Classe {classe.nom} modifiée - {', '.join(parts_msg)}.")

                    else:

                        messages.success(request, f'Classe {classe.nom} modifiée.')

                    
                    objet_execute = True

                    log_audit(request.user, 'update', 'Classe', classe, 'Modification approuvée', request)

                else:

                    messages.error(request, f'Classe introuvable (ID: {demande.objet_id}).')

            else:

                messages.error(request, 'ID de la classe manquant dans la demande.')

                    
        elif demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                classe = Classe.objects.filter(pk=demande.objet_id).first()

                if classe:

                    nom_classe = str(classe)

                    classe.delete()

                    objet_execute = True

                    messages.success(request, f'Classe supprimée.')

                    log_audit(request.user, 'delete', 'Classe', None, f'Suppression approuvée: {nom_classe}', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.PROFESSEUR:

        from academics.models import Professeur

        if demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

            if demande.objet_id:

                prof = Professors.objects.filter(pk=demande.objet_id).first()

                if prof:

                    details = demande.details_apos

                    if 'Nom:' in details:

                        prof.nom = details.split('Nom:')[1].split('\n')[0].strip()

                    if 'Prénom:' in details:

                        prof.prenom = details.split('Prénom:')[1].split('\n')[0].strip()

                    if 'Email:' in details:

                        prof.email = details.split('Email:')[1].split('\n')[0].strip()

                    if 'Spécialité:' in details:

                        prof.specialite = details.split('Spécialité:')[1].split('\n')[0].strip()

                    prof.save()

                    objet_execute = True

                    messages.success(request, f'Professeur {prof.nom} {prof.prenom} modifié.')

                    log_audit(request.user, 'update', 'Professeur', prof, 'Modification approuvée', request)

                    
        elif demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                prof = Professors.objects.filter(pk=demande.objet_id).first()

                if prof:

                    nom_prof = str(prof)

                    prof.delete()

                    objet_execute = True

                    messages.success(request, f'Professeur supprimé.')

                    log_audit(request.user, 'delete', 'Professeur', None, f'Suppression approuvée: {nom_prof}', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.FRAIS:

        from finances.models import FraisScolaire, AnneeScolaire

        if demande.type_action == DemandeApprobation.TypeAction.CREATION:

            type_frais = demande.details.split('Type:')[1].split('\n')[0].strip() if 'Type:' in demande.details else 'autre'

            montant = 0

            if 'Montant:' in demande.details:

                try:

                    montant = float(demande.details.split('Montant:')[1].split('FCFA')[0].strip())

                except:

                    pass

            
            frais = FraisScolaire.objects.create(

                type_frais=type_frais,

                montant=montant,

                mode_application='detaille'

            )

            demande.objet_id = frais.pk

            objet_execute = True

            messages.success(request, 'Frais créés avec succès.')

            log_audit(request.user, 'create', 'FraisScolaire', frais, 'Frais créés', request)

            
        elif demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

            if demande.objet_id:

                frais = FraisScolaire.objects.filter(pk=demande.objet_id).first()

                if frais:

                    details = demande.details_apos

                    if 'Montant:' in details:

                        try:

                            frais.montant = float(details.split('Montant:')[1].split('FCFA')[0].strip())

                        except:

                            pass

                    if 'Type:' in details:

                        frais.type_frais = details.split('Type:')[1].split('\n')[0].strip()

                    frais.save()

                    objet_execute = True

                    messages.success(request, 'Frais modifiés.')

                    log_audit(request.user, 'update', 'FraisScolaire', frais, 'Frais modifiés', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.CHARGE:

        from finances.models import ChargeFixe, ChargeOperationnelle

        if demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                charge_fixe = ChargeFixe.objects.filter(pk=demande.objet_id).first()

                charge_op = None

                if not charge_fixe:

                    charge_op = ChargeOperationnelle.objects.filter(pk=demande.objet_id).first()

                
                if charge_fixe:

                    nom_charge = str(charge_fixe)

                    charge_fixe.delete()

                    objet_execute = True

                    messages.success(request, f'Charge fixe supprimée.')

                    log_audit(request.user, 'delete', 'ChargeFixe', None, f'Suppression approuvée: {nom_charge}', request)

                elif charge_op:

                    nom_charge = str(charge_op)

                    charge_op.delete()

                    objet_execute = True

                    messages.success(request, f'Charge opérationnelle supprimée.')

                    log_audit(request.user, 'delete', 'ChargeOperationnelle', None, f'Suppression approuvée: {nom_charge}', request)

    
    elif demande.type_objet == DemandeApprobation.TypeObjet.PERSONNEL:

        from finances.models import Personnel

        if demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

            if demande.objet_id:

                personnel = Personnel.objects.filter(pk=demande.objet_id).first()

                if personnel:

                    nom_personnel = str(personnel)

                    personnel.delete()

                    objet_execute = True

                    messages.success(request, f'Personnel supprimé.')

                    log_audit(request.user, 'delete', 'Personnel', None, f'Suppression approuvée: {nom_personnel}', request)

    
    if not objet_execute:

        messages.warning(request, f'Aucun objet exécuté pour cette demande. Type: {demande.type_objet}, Action: {demande.type_action}')

    
    demande.statut = DemandeApprobation.Statut.APPROUVE

    demande.approbateur = request.user

    demande.date_traitement = timezone.now()

    demande.observations = observations

    demande.save()

    
    log_audit(request.user, 'update', 'DemandeApprobation', demande, f'Approuvé: {observations}', request)

    
    type_action_display = demande.get_type_action_display().lower()

    type_objet_display = demande.get_type_objet_display().lower()

    objet_libelle = demande.objet_repr or 'l\'objet'

    
    if demande.type_action == DemandeApprobation.TypeAction.SUPPRESSION:

        message_notification = f"Votre demande de {type_action_display} de {objet_libelle} a été APPROUVÉE par {request.user.get_full_name() or request.user.username}."

    elif demande.type_action == DemandeApprobation.TypeAction.MODIFICATION:

        message_notification = f"Votre demande de {type_action_display} de {objet_libelle} a été APPROUVÉE par {request.user.get_full_name() or request.user.username}."

    else:

        message_notification = f"Votre demande de {type_action_display} {type_objet_display} ({objet_libelle}) a été APPROUVÉE par {request.user.get_full_name() or request.user.username}."

    
    if objet_execute:

        message_notification += "\n\nL'opération a été exécutée avec succès."

    if observations:

        message_notification += f"\n\nObservations: {observations}"

    
    Notification.creer_notification(

        destinataire=demande.demandeur,

        type_notification=Notification.TypeNotification.AUTRE,

        titre=f"Demande approuvée - {type_action_display} {type_objet_display}",

        message=message_notification,

        expediteur=request.user

    )

    
    messages.success(request, f'Demande approuvée. Le demandeur a été notifié.')

    return redirect('accounts:demande_list')


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def demande_rejeter(request, pk):
    demande = get_object_or_404(DemandeApprobation, pk=pk)

    
    if demande.statut != DemandeApprobation.Statut.EN_ATTENTE:

        messages.error(request, 'Cette demande a déjà été traitée.')

        return redirect('accounts:demande_list')

    
    observations = request.POST.get('observations', '')

    
    if demande.type_objet == DemandeApprobation.TypeObjet.CONTRAINTE and demande.objet_id:

        from academics.models import ContrainteHoraire

        try:

            contrainte = ContrainteHoraire.objects.get(pk=demande.objet_id)

            contrainte.delete()

        except ContrainteHoraire.DoesNotExist:

            pass

    
    demande.statut = DemandeApprobation.Statut.REJETE

    demande.approbateur = request.user

    demande.date_traitement = timezone.now()

    demande.observations = observations

    demande.save()

    
    log_audit(request.user, 'update', 'DemandeApprobation', demande, f'Rejeté: {observations}', request)

    
    Notification.creer_notification(

        destinataire=demande.demandeur,

        type_notification=Notification.TypeNotification.AUTRE,

        titre=f"Demande rejetée - {demande.get_type_action_display()} {demande.get_type_objet_display()}",

        message=f"Votre demande de {demande.get_type_action_display()} de {demande.objet_repr or demande.get_type_objet_display()} a été REJETÉE par {request.user.get_full_name() or request.user.username}.\n\nMotif du rejet: {observations or 'Aucun motif fourni'}",

        expediteur=request.user

    )

    
    messages.warning(request, 'Demande rejetée. Le demandeur a été notifié.')

    return redirect('accounts:demande_list')


def password_recovery(request):

    if request.user.is_authenticated:

        return redirect('dashboard')

    
    if request.method == 'POST':

        first_name = request.POST.get('first_name', '').strip()

        last_name = request.POST.get('last_name', '').strip()

        telephone = request.POST.get('telephone', '').strip()

        email = request.POST.get('email', '').strip().lower()

        
        user = User.objects.filter(

            first_name__iexact=first_name,

            last_name__iexact=last_name,

            telephone__iexact=telephone,

            email__iexact=email,

            is_active=True

        ).first()

        
        if not user:

            messages.error(request, 'Les informations fournies ne correspondent à aucun utilisateur dans le système.')

            return render(request, 'accounts/password_recovery.html')

        
        from .models import PasswordResetCode

        PasswordResetCode.create_reset(user)

        
        request.session['reset_user_id'] = user.id

        return redirect('accounts:password_recovery_verify')

    
    return render(request, 'accounts/password_recovery.html')


def password_recovery_verify(request):

    if request.user.is_authenticated:

        return redirect('dashboard')

    
    user_id = request.session.get('reset_user_id')

    if not user_id:

        messages.error(request, 'Session expirée. Veuillez recommencer.')

        return redirect('accounts:password_recovery')

    
    user = get_object_or_404(User, pk=user_id)

    
    if request.method == 'POST':

        code = request.POST.get('code', '').strip()

        
        from .models import PasswordResetCode

        is_valid, error = PasswordResetCode.verify_code(user, code)

        
        if not is_valid:

            messages.error(request, error)

            return render(request, 'accounts/password_recovery_verify.html', {'email': user.email})

        
        request.session['reset_code_verified'] = True

        return redirect('accounts:password_recovery_reset')

    
    return render(request, 'accounts/password_recovery_verify.html', {'email': user.email})


def password_recovery_reset(request):

    if request.user.is_authenticated:

        return redirect('dashboard')

    
    user_id = request.session.get('reset_user_id')

    if not user_id or not request.session.get('reset_code_verified'):

        messages.error(request, 'Session expirée. Veuillez recommencer.')

        return redirect('accounts:password_recovery')

    
    user = get_object_or_404(User, pk=user_id)

    
    if request.method == 'POST':

        new_username = request.POST.get('username', '').strip()

        password1 = request.POST.get('password1', '')

        password2 = request.POST.get('password2', '')

        
        if password1 != password2:

            messages.error(request, 'Les mots de passe ne correspondent pas.')

            return render(request, 'accounts/password_recovery_reset.html')

        
        if len(password1) < 8:

            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')

            return render(request, 'accounts/password_recovery_reset.html')

        
        if new_username:

            if User.objects.exclude(pk=user.id).filter(username=new_username).exists():

                messages.error(request, 'Ce nom d\'utilisateur est déjà utilisé.')

                return render(request, 'accounts/password_recovery_reset.html')

            user.username = new_username

        
        user.set_password(password1)

        user.save()

        
        from .models import PasswordResetCode

        PasswordResetCode.objects.filter(user=user, used=False).update(used=True)

        
        request.session.flush()

        
        messages.success(request, 'Identifiants réinitialisés avec succès. Veuillez vous connecter.')

        return redirect('accounts:login')

    
    return render(request, 'accounts/password_recovery_reset.html')


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_modification_list(request):
    """Liste des demandes de modification de permissions"""

    statut = request.GET.get('statut')

    
    if statut:

        modifications = PermissionModification.objects.filter(statut=statut)

    else:

        modifications = PermissionModification.objects.all()

    
    modifications = modifications.select_related('module', 'demandeur').order_by('-created_at')

    
    return render(request, 'accounts/permission_modification_list.html', {

        'modifications': modifications,

        'statut': statut

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_modification_detail(request, pk):
    """Détail d'une demande de modification de permission"""

    modification = get_object_or_404(PermissionModification, pk=pk)

    
    return render(request, 'accounts/permission_modification_detail.html', {

        'modification': modification

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_modification_approuver(request, pk):
    """Approuver une demande de modification de permission"""

    modification = get_object_or_404(PermissionModification, pk=pk, statut=PermissionModification.Statut.EN_ATTENTE)

    
    commentaire = request.POST.get('commentaire', '')

    modification.approuver(request.user, commentaire)

    
    messages.success(request, f'Modification approuvée pour {modification.module.nom}')

    return redirect('accounts:permission_modification_list')


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_modification_rejeter(request, pk):
    """Rejeter une demande de modification de permission"""

    modification = get_object_or_404(PermissionModification, pk=pk, statut=PermissionModification.Statut.EN_ATTENTE)

    
    commentaire = request.POST.get('commentaire', '')

    modification.rejeter(request.user, commentaire)

    
    messages.warning(request, f'Modification rejetée pour {modification.module.nom}')

    return redirect('accounts:permission_modification_list')


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_utilisateur_list(request):
    """Liste des permissions utilisateur"""

    utilisateur_id = request.GET.get('utilisateur')

    
    if utilisateur_id:

        permissions = PermissionUtilisateur.objects.filter(utilisateur_id=utilisateur_id)

    else:

        permissions = PermissionUtilisateur.objects.all()

    
    permissions = permissions.select_related('utilisateur', 'module').order_by('-created_at')

    
    all_users = User.objects.filter(is_active=True).order_by('username')

    
    return render(request, 'accounts/permission_utilisateur_list.html', {

        'permissions': permissions,

        'utilisateur_id': utilisateur_id,

        'all_users': all_users

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_utilisateur_create(request):
    """Créer une permission utilisateur"""

    if request.method == 'POST':

        utilisateur_id = request.POST.get('utilisateur')

        module_id = request.POST.get('module')

        actions = request.POST.getlist('actions')

        niveau = request.POST.get('niveau')

        est_temporaire = request.POST.get('est_temporaire') == 'on'

        date_debut = request.POST.get('date_debut')

        date_fin = request.POST.get('date_fin')

        
        perm = PermissionUtilisateur.objects.create(

            utilisateur_id=utilisateur_id,

            module_id=module_id,

            actions=actions,

            niveau=niveau,

            est_temporaire=est_temporaire,

            date_debut=date_debut or None,

            date_fin=date_fin or None,

            created_by=request.user

        )

        
        messages.success(request, 'Permission créée avec succès')

        return redirect('accounts:permission_utilisateur_list')

    
    users = User.objects.filter(is_active=True).order_by('username')

    modules = Module.objects.filter(est_actif=True).select_related('service').order_by('service__nom', 'nom')

    
    return render(request, 'accounts/permission_utilisateur_form.html', {

        'users': users,

        'modules': modules

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_utilisateur_edit(request, pk):
    """Modifier une permission utilisateur"""

    perm = get_object_or_404(PermissionUtilisateur, pk=pk)

    
    if request.method == 'POST':

        perm.actions = request.POST.getlist('actions')

        perm.niveau = request.POST.get('niveau')

        perm.est_temporaire = request.POST.get('est_temporaire') == 'on'

        perm.date_debut = request.POST.get('date_debut') or None

        perm.date_fin = request.POST.get('date_fin') or None

        perm.est_actif = request.POST.get('est_actif') == 'on'

        perm.save()

        
        messages.success(request, 'Permission modifiée avec succès')

        return redirect('accounts:permission_utilisateur_list')

    
    users = User.objects.filter(is_active=True).order_by('username')

    modules = Module.objects.filter(est_actif=True).select_related('service').order_by('service__nom', 'nom')

    
    return render(request, 'accounts/permission_utilisateur_form.html', {

        'permission': perm,

        'users': users,

        'modules': modules

    })


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def permission_utilisateur_delete(request, pk):
    """Supprimer une permission utilisateur"""

    perm = get_object_or_404(PermissionUtilisateur, pk=pk)

    perm.delete()

    
    messages.success(request, 'Permission supprimée avec succès')

    return redirect('accounts:permission_utilisateur_list')


@login_required
@login_required
def view_func(request):
    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
def user_permissions_detail(request, user_id):
    """Affiche les permissions détaillées d'un utilisateur"""

    user = get_object_or_404(User, pk=user_id)

    
    # Obtenir tous les services avec leurs modules

    from accounts.models import Service, Module

    services = Service.objects.filter(est_actif=True).prefetch_related('modules').order_by('ordre')

    
    # Obtenir les permissions utilisateur (toutes, actives et désactivées)

    user_perms = PermissionUtilisateur.objects.filter(utilisateur=user)

    user_perms_dict = {p.module_id: p for p in user_perms}

    
    # Obtenir les permissions de rôle

    role_perms = Permission.objects.filter(role=user.role)

    role_perms_dict = {p.module_id: p for p in role_perms}

    
    # Obtenir les modules personnalisés

    custom_modules = user.modules_permissions.all()

    custom_modules_ids = set(custom_modules.values_list('id', flat=True))

    
    service_data = []

    for service in services:

        modules_data = []

        for module in service.modules.filter(est_actif=True):

            user_perm = user_perms_dict.get(module.id)

            role_perm = role_perms_dict.get(module.id)

            is_custom = module.id in custom_modules_ids

            
            # Déterminer l'état de la permission

            # Pour direction/superadmin: accès par défaut, sauf si désactivé explicitement

            if user.is_direction() or user.is_superadmin():

                # Vérifier si désactivé (est_actif=False) OU si actions vides avec permission existante

                if user_perm and (not user_perm.est_actif or (user_perm.est_actif and not user_perm.actions)):

                    # Désactivé explicitement

                    has_permission = False

                    is_disabled = True

                    actions = []

                elif user_perm and user_perm.actions:

                    # Permission utilisateur active avec actions

                    has_permission = True

                    is_disabled = False

                    actions = list(user_perm.actions)

                else:

                    # Pas de restriction - accès par défaut

                    has_permission = True

                    is_disabled = False

                    actions = list(role_perm.actions) if role_perm else []

            else:

                # Autres rôles: basé sur les permissions de rôle

                if user_perm and user_perm.est_actif and user_perm.actions:

                    # Permission utilisateur active

                    has_permission = True

                    is_disabled = False

                    actions = list(user_perm.actions)

                elif user_perm and not user_perm.est_actif:

                    # Permission désactivée

                    has_permission = False

                    is_disabled = True

                    actions = []

                elif role_perm:

                    # Pas de permission utilisateur mais permission de rôle existe

                    has_permission = bool(role_perm.actions)

                    is_disabled = False  # Pas de record, donc pas de bouton "désactiver" possible

                    actions = list(role_perm.actions)

                elif is_custom:

                    has_permission = True

                    is_disabled = False

                    actions = ['read', 'write', 'update', 'delete']

                else:

                    # Pas de permission du tout - proposer d'activer

                    has_permission = False

                    is_disabled = True  # Utiliser is_disabled pour afficher le bouton "Activer"

                    actions = []

            
            modules_data.append({

                'module': module,

                'has_permission': has_permission,

                'is_disabled': is_disabled,

                'actions': actions,

                'is_custom': is_custom,

                'user_perm': user_perm,

                'role_perm': role_perm

            })

        
        service_data.append({

            'service': service,

            'modules': modules_data

        })

    
    return render(request, 'accounts/user_permissions_detail.html', {

        'target_user': user,

        'service_data': service_data

    })



@login_required
@login_required
def view_func(request):
    """Active ou désactive l'accès à un module pour un utilisateur"""

    # Manual check instead of decorator

    if not (request.user.is_direction() or request.user.is_superadmin()):

        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")

        return redirect('accounts:user_list')

    
    user = get_object_or_404(User, pk=user_id)

    module = get_object_or_404(Module, pk=module_id)

    
    # Handle both POST and GET

    action = request.POST.get('action') or request.GET.get('action')

    enable_value = request.POST.get('enable') or request.GET.get('enable', '')

    
    print(f"DEBUG toggle: action={action}, enable={enable_value}, user={user.username}, module={module.code}")

    
    if action == 'toggle_module':

        perm = PermissionUtilisateur.objects.filter(utilisateur=user, module=module).first()

        
        enable = enable_value.lower() == 'true'

        
        if enable:

            if not perm:

                perm = PermissionUtilisateur.objects.create(

                    utilisateur=user,

                    module=module,

                    actions=['read', 'write', 'update', 'delete'],

                    niveau='admin',

                    created_by=request.user

                )

                print(f"DEBUG: Created new permission for {module.code}")

                log_audit(request.user, 'create', 'PermissionUtilisateur', perm, f'Activation accès module {module.code} pour {user.username}', request)

            else:

                perm.est_actif = True

                if not perm.actions:

                    perm.actions = ['read', 'write', 'update', 'delete']

                perm.save()

                print(f"DEBUG: Updated existing permission, est_actif={perm.est_actif}")

                log_audit(request.user, 'update', 'PermissionUtilisateur', perm, f'Activation accès module {module.code} pour {user.username}', request)

            messages.success(request, f"Accès au module {module.nom} activé")

        else:

            if perm:

                perm.est_actif = False

                perm.save()

                print(f"DEBUG: Disabled permission")

                log_audit(request.user, 'update', 'PermissionUtilisateur', perm, f'Désactivation accès module {module.code} pour {user.username}', request)

            else:

                perm = PermissionUtilisateur.objects.create(

                    utilisateur=user,

                    module=module,

                    actions=[],

                    niveau='standard',

                    est_actif=False,

                    created_by=request.user

                )

                print(f"DEBUG: Created disabled permission")

                log_audit(request.user, 'create', 'PermissionUtilisateur', perm, f'Désactivation accès module {module.code} pour {user.username}', request)

            messages.success(request, f"Accès au module {module.nom} désactivé")

        
        return redirect('accounts:user_permissions_detail', user_id=user_id)

    
    if action == 'update_actions':

        new_actions = request.POST.getlist('actions')

        perm = PermissionUtilisateur.objects.filter(utilisateur=user, module=module).first()

        
        if new_actions:

            if perm:

                perm.actions = new_actions

                perm.est_actif = True

                perm.save()

                log_audit(request.user, 'update', 'PermissionUtilisateur', perm, f'Modification actions: {new_actions} pour {user.username} sur {module.code}', request)

            else:

                perm = PermissionUtilisateur.objects.create(

                    utilisateur=user,

                    module=module,

                    actions=new_actions,

                    niveau='complet',

                    est_actif=True,

                    created_by=request.user

                )

                log_audit(request.user, 'create', 'PermissionUtilisateur', perm, f'Création permissions: {new_actions} pour {user.username} sur {module.code}', request)

            messages.success(request, f"Actions mises à jour pour {module.nom}")

        else:

            messages.warning(request, "Veuillez sélectionner au moins une action.")

        
        return redirect('accounts:user_permissions_detail', user_id=user_id)

    
    if action == 'remove_custom':

        perm = PermissionUtilisateur.objects.filter(utilisateur=user, module=module).first()

        if perm:

            log_audit(request.user, 'delete', 'PermissionUtilisateur', perm, f'Suppression permission pour {user.username} sur {module.code}', request)

            perm.delete()

        messages.success(request, f"Permission personnalisée supprimée pour {module.nom}")

        return redirect('accounts:user_permissions_detail', user_id=user_id)

    
    return redirect('accounts:user_permissions_detail', user_id=user_id)


@login_required
def user_create(request):
    if not request.user.has_module_permission('user_management', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur cree.')
            return redirect('accounts:user_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/user_form.html', {'form': form})


@login_required
def user_edit(request, pk):
    if not request.user.has_module_permission('user_management', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur modifie.')
            return redirect('accounts:user_list')
    else:
        form = UserChangeForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {'form': form, 'user_obj': user})


@login_required
def user_delete(request, pk):
    if not request.user.has_module_permission('user_management', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprime.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user_obj': user})


@login_required
def user_approve(request, pk):
    if not request.user.has_module_permission('user_management', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    messages.success(request, f'Utilisateur {user.username} approuve.')
    return redirect('accounts:user_list')


@login_required
def user_toggle_active(request, pk):
    if not request.user.has_module_permission('user_management', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'active' if user.is_active else 'inactive'
    messages.success(request, f'Utilisateur {user.username} {status}.')
    return redirect('accounts:user_list')


@login_required
def user_show_password(request, pk):
    if not request.user.has_module_permission('user_management', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_password.html', {'user_obj': user})


@login_required
def user_reset_password(request, pk):
    if not request.user.has_module_permission('user_management', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    new_password = request.POST.get('new_password')
    if new_password:
        user.set_password(new_password)
        user.save()
        messages.success(request, f'Mot de passe de {user.username} reinitialise.')
    else:
        messages.error(request, 'Veuillez entrer un nouveau mot de passe.')
    return redirect('accounts:user_list')


@login_required
def user_permission_toggle(request, user_id, module_code):
    if not request.user.has_module_permission('permissions_utilisateur', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    module = get_object_or_404(Module, code=module_code)
    action = request.POST.get('action', 'toggle_module')
    
    if action == 'toggle_module':
        enable = request.POST.get('enable', 'true') == 'true'
        
        perm, created = PermissionUtilisateur.objects.get_or_create(
            utilisateur=user,
            module=module,
            defaults={'est_actif': True, 'actions': ['read']}
        )
        
        perm.est_actif = enable
        perm.save()
        
    elif action == 'update_actions':
        actions = request.POST.getlist('actions')
        
        perm, created = PermissionUtilisateur.objects.get_or_create(
            utilisateur=user,
            module=module,
            defaults={'est_actif': True, 'actions': actions}
        )
        perm.est_actif = True
        perm.actions = actions
        perm.save()
        
    elif action == 'remove_custom':
        PermissionUtilisateur.objects.filter(utilisateur=user, module=module).delete()
    
    return redirect('accounts:user_permissions_detail', user_id=user_id)


@login_required
def notification_list(request):
    if not request.user.has_module_permission('notifications', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    notifications = Notification.objects.filter(destinataire=request.user).order_by('-date_creation')[:50]
    return render(request, 'accounts/notification_list.html', {'notifications': notifications})


@login_required
def notification_detail(request, pk):
    if not request.user.has_module_permission('notifications', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notification.est_lue = True
    notification.save()
    return render(request, 'accounts/notification_detail.html', {'notification': notification})


@login_required
def notification_mark_all_read(request):
    if not request.user.has_module_permission('notifications', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    Notification.objects.filter(destinataire=request.user).update(est_lue=True)
    messages.success(request, 'Toutes les notifications marquees comme lues.')
    return redirect('accounts:notification_list')


@login_required
def message_list(request):
    if not request.user.has_module_permission('messages', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    messages_list = Message.objects.filter(destinataire=request.user).order_by('-date_creation')[:50]
    return render(request, 'accounts/message_list.html', {'messages': messages_list})


@login_required
def message_detail(request, pk):
    if not request.user.has_module_permission('messages', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    msg = get_object_or_404(Message, pk=pk, destinataire=request.user)
    msg.est_lu = True
    msg.save()
    return render(request, 'accounts/message_detail.html', {'message': msg})


@login_required
def message_create(request):
    if not request.user.has_module_permission('messages', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        destinataire_id = request.POST.get('destinataire')
        
        if contenu and destinataire_id:
            destinataire = get_object_or_404(User, pk=destinataire_id)
            Message.objects.create(
                expediteur=request.user,
                destinataire=destinataire,
                contenu=contenu
            )
            messages.success(request, 'Message envoye.')
            return redirect('accounts:message_list')
    
    users = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
    return render(request, 'accounts/message_form.html', {'users': users})


@login_required
def message_mark_all_read(request):
    if not request.user.has_module_permission('messages', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    Message.objects.filter(destinataire=request.user).update(est_lu=True)
    messages.success(request, 'Tous les messages marques comme lus.')
    return redirect('accounts:message_list')


@login_required
def locked_accounts(request):
    if not request.user.has_module_permission('user_management', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from django.utils import timezone
    from accounts.models import LoginAttempt
    
    locked = LoginAttempt.objects.filter(
        locked_until__isnull=False,
        locked_until__gt=timezone.now()
    ).order_by('locked_until')
    
    return render(request, 'accounts/locked_accounts.html', {'locked_accounts': locked})


@login_required
def chat_inbox(request):
    if not request.user.has_module_permission('chat', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    return render(request, 'accounts/chat_inbox.html')


@login_required
def chat_conversation(request, pk):
    if not request.user.has_module_permission('chat', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/chat_conversation.html', {'user': user})


@login_required
def chat_new(request):
    if not request.user.has_module_permission('chat', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    return redirect('accounts:chat_inbox')
