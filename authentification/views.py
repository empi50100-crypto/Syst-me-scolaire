from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
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

from .models import Utilisateur, log_audit, Notification, Message, TentativeConnexion, ProfilPermission, PermissionPersonnalisee, CodeReinitialisation
from .forms import UserRegistrationForm, UserCreationForm, UserChangeForm


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
    
    users = Utilisateur.objects.all().order_by('-date_joined')
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
    notifications = request.user.notifications.all().order_by('-date_creation')[:50]
    return render(request, 'authentification/notification_list.html', {'notifications': notifications})


@login_required
def message_list(request):
    messages_recus = request.user.messages_recus.all().order_by('-date_envoi')[:50]
    return render(request, 'authentification/message_list.html', {'messages_recus': messages_recus})


@login_required
def message_create(request):
    if request.method == 'POST':
        dest_id = request.POST.get('destinataire')
        sujet = request.POST.get('sujet')
        contenu = request.POST.get('contenu')
        if dest_id:
            Message.objects.create(auteur=request.user, destinataire_id=dest_id, sujet=sujet, contenu=contenu)
            messages.success(request, 'Message envoyé.')
            return redirect('authentification:message_list')
    
    utilisateurs = Utilisateur.objects.filter(is_active=True).exclude(pk=request.user.pk)
    return render(request, 'authentification/message_form.html', {'utilisateurs': utilisateurs})


@login_required
def user_permissions_detail(request, pk):
    if not request.user.is_superadmin:
        messages.error(request, "Vous n'avez pas l'autorisation de gérer les permissions.")
        return redirect('authentification:user_list')
    
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        # Mise à jour des permissions personnalisées
        permission_codes = request.POST.getlist('permissions')
        
        # Supprimer les anciennes permissions
        PermissionPersonnalisee.objects.filter(utilisateur=utilisateur).delete()
        
        # Créer les nouvelles permissions
        for code in permission_codes:
            PermissionPersonnalisee.objects.create(
                utilisateur=utilisateur,
                module_code=code,
                peut_lire='lecture' in request.POST.get(f'perm_{code}', ''),
                peut_creer='creation' in request.POST.get(f'perm_{code}', ''),
                peut_modifier='modification' in request.POST.get(f'perm_{code}', ''),
                peut_supprimer='suppression' in request.POST.get(f'perm_{code}', '')
            )
        
        messages.success(request, f'Permissions de {utilisateur.get_full_name} mises à jour.')
        return redirect('authentification:user_list')
    
    # Récupérer les permissions actuelles
    permissions_existantes = {
        p.module_code: p for p in PermissionPersonnalisee.objects.filter(utilisateur=utilisateur)
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
                    # Permissions personnalisées définies
                    if perm.peut_lire:
                        actions.append('read')
                    if perm.peut_creer:
                        actions.append('write')
                    if perm.peut_modifier:
                        actions.append('update')
                    if perm.peut_supprimer:
                        actions.append('delete')
                elif is_superadmin_or_direction:
                    # Superadmin/Direction sans custom permission = full access
                    actions = ['read', 'write', 'update', 'delete']
            
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
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_module':
            # Activer/désactiver l'accès à un module
            perm, created = PermissionPersonnalisee.objects.get_or_create(
                utilisateur=utilisateur,
                module_code=module_code,
                defaults={'peut_lire': True, 'est_actif': True}
            )
            if not created:
                perm.est_actif = not perm.est_actif
                perm.save()
            
            status = 'activé' if perm.est_actif else 'désactivé'
            messages.success(request, f"Accès au module {module_code} {status} pour {utilisateur.get_full_name}.")
        
        elif action == 'update_actions':
            # Mettre à jour les actions (lecture, création, modification, suppression)
            perm, created = PermissionPersonnalisee.objects.get_or_create(
                utilisateur=utilisateur,
                module_code=module_code,
                defaults={'est_actif': True}
            )
            
            actions = request.POST.getlist('actions')
            perm.peut_lire = 'read' in actions
            perm.peut_creer = 'create' in actions
            perm.peut_modifier = 'update' in actions
            perm.peut_supprimer = 'delete' in actions
            perm.save()
            
            messages.success(request, f"Permissions du module {module_code} mises à jour pour {utilisateur.get_full_name}.")
    
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
            utilisateur.save()
            log_audit(request.user, 'password_reset', utilisateur, f"Réinitialisation du mot de passe de {utilisateur.username}")
            messages.success(request, f'Mot de passe de {utilisateur.get_full_name} réinitialisé avec succès.')
        else:
            messages.error(request, 'Veuillez entrer un nouveau mot de passe.')
        return redirect('authentification:user_list')
    
    return redirect('authentification:user_list')
