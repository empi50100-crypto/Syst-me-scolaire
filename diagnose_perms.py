"""Script de diagnostic des permissions"""
import os
import sys
import django

sys.path.insert(0, r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Module, Permission, PermissionUtilisateur

def diagnose_user_permissions(username):
    print(f"\n{'='*60}")
    print(f"Diagnostic pour: {username}")
    print(f"{'='*60}")
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"Utilisateur '{username}' non trouvé!")
        return
    
    print(f"\nRôle: {user.role}")
    print(f"is_superadmin: {user.is_superadmin()}")
    print(f"is_direction: {user.is_direction()}")
    
    print(f"\nModules actifs dans la DB: {Module.objects.count()}")
    
    print(f"\n--- Permissions de Rôle (Permission) ---")
    role_perms = Permission.objects.filter(role=user.role)
    if role_perms.exists():
        for p in role_perms:
            print(f"  {p.module.code}: {p.actions}")
    else:
        print("  Aucune permission de rôle trouvée!")
    
    print(f"\n--- Permissions Utilisateur (PermissionUtilisateur) ---")
    user_perms = PermissionUtilisateur.objects.filter(utilisateur=user)
    if user_perms.exists():
        for p in user_perms:
            print(f"  {p.module.code}: actif={p.est_actif}, is_valid={p.is_valid()}, actions={p.actions}")
    else:
        print("  Aucune permission utilisateur personnalisée")
    
    print(f"\n--- Test has_module_permission pour quelques modules clés ---")
    test_modules = ['fiche_notes', 'bulletins', 'presence_list', 'saisie_notes', 'eleve_list', 'classe_list']
    for mod_code in test_modules:
        try:
            mod = Module.objects.get(code=mod_code)
            result = user.has_module_permission(mod_code, 'read')
            print(f"  {mod_code}: {result}")
        except Module.DoesNotExist:
            print(f"  {mod_code}: MODULE N'EXISTE PAS!")

if __name__ == '__main__':
    print("DIAGNOSTIC DES PERMISSIONS")
    print("="*60)
    
    usernames = ['admin', 'AM', 'secretariat', 'surveillant', 'Comptable', 'prof']
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            diagnose_user_permissions(username)
        except User.DoesNotExist:
            print(f"\nUtilisateur '{username}' non trouvé")
    
    print("\n\n" + "="*60)
    print("MODULES DANS LA BASE DE DONNÉES:")
    print("="*60)
    for mod in Module.objects.all():
        print(f"  {mod.code}: {mod.nom} (service: {mod.service.code})")
