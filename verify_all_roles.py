import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, Module, Permission
from django.urls import resolve

print("=" * 70)
print("VERIFICATION COMPLETE DU SYSTEME DE PERMISSIONS")
print("=" * 70)

# Get all roles
roles = ['superadmin', 'direction', 'secretaire', 'comptable', 'professeur', 'surveillance', 'agent_securite']

for role in roles:
    user = User.objects.filter(role=role).first()
    if not user:
        print(f"\n[AVERTISSEMENT] Aucun utilisateur pour le role: {role}")
        continue
    
    print(f"\n{'='*60}")
    print(f"UTILISATEUR: {user.username} | ROLE: {role}")
    print(f"{'='*60}")
    
    # Check accessible modules (sidebar)
    accessible = user.get_accessible_modules()
    print(f"Modules accessibles (sidebar): {accessible.count()}")
    
    if accessible.count() == 0:
        print("  [PROBLEME] Aucun module accessible!")
        print("  Verification des permissions de role...")
        role_perms = Permission.objects.filter(role=role).count()
        print(f"  Permissions de role definies: {role_perms}")
        
        # Check if there are any PermissionUtilisateur that might be blocking
        pu_blocking = user.modules_permissions.count()
        print(f"  Permissions personnalisees: {pu_blocking}")
        continue
    
    print(f"\n  Verification des URLs:")
    errors = []
    for m in accessible:
        try:
            match = resolve(m.url)
            print(f"    OK: {m.code} -> {m.url}")
        except Exception as e:
            print(f"    ERREUR: {m.code}: {m.url} - {e}")
            errors.append(m.code)
    
    if errors:
        print(f"\n  [AVERTISSEMENT] URLs invalides: {errors}")
    
    # Test has_module_permission for key modules
    test_modules = ['eleve_list', 'classe_list', 'annee_scolaire', 'bulletins', 'saisie_notes', 'presence_list']
    print(f"\n  Test has_module_permission:")
    for mod in test_modules:
        has_read = user.has_module_permission(mod, 'read')
        has_write = user.has_module_permission(mod, 'write')
        if has_read or has_write:
            print(f"    OK {mod}: read={has_read}, write={has_write}")
        else:
            print(f"      -- {mod}: read={has_read}, write={has_write}")

print("\n" + "=" * 70)
print("RESUME DES PROBLEMES")
print("=" * 70)

# Check which roles have no permissions
for role in roles:
    user = User.objects.filter(role=role).first()
    if not user:
        print(f"[ERREUR] Role '{role}': Aucun utilisateur")
        continue
    
    accessible = user.get_accessible_modules()
    role_perms = Permission.objects.filter(role=role).count()
    
    if accessible.count() == 0 and role_perms == 0:
        print(f"[ERREUR] Role '{role}': Pas de permissions de role definies")

print("\nVerification terminee!")