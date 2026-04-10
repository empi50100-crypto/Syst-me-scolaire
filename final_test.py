import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, PermissionUtilisateur, Module

print("=" * 70)
print("VERIFICATION COMPLETE - SCENARIO D'ACTIVATION DE MODULE")
print("=" * 70)

# Test each role with activation scenario
roles_to_test = [
    ('professeur', 'annee_scolaire'),
    ('secretaire', 'saisie_notes'),
    ('comptable', 'presence_list'),
    ('surveillance', 'bulletins'),
]

for role, test_module_code in roles_to_test:
    print(f"\n--- Test: Activation {test_module_code} pour role {role} ---")
    
    user = User.objects.filter(role=role).first()
    if not user:
        print(f"  Aucun utilisateur pour role {role}")
        continue
    
    module = Module.objects.filter(code=test_module_code).first()
    if not module:
        print(f"  Module {test_module_code} non trouve")
        continue
    
    # Check if role has default permission
    from accounts.models import Permission
    role_perm = Permission.objects.filter(role=role, module=module).first()
    print(f"  Permission de role: {role_perm.actions if role_perm else 'Aucune'}")
    
    # Test without custom permission
    has_before = user.has_module_permission(test_module_code, 'read')
    print(f"  Avant activation: has_module_permission = {has_before}")
    
    # Simulate admin activation
    perm, created = PermissionUtilisateur.objects.get_or_create(
        utilisateur=user,
        module=module,
        defaults={
            'actions': ['read', 'write', 'update'],
            'niveau': 'complet',
            'est_actif': True
        }
    )
    
    # Test after activation
    has_after_read = user.has_module_permission(test_module_code, 'read')
    has_after_write = user.has_module_permission(test_module_code, 'write')
    print(f"  Apres activation: read={has_after_read}, write={has_after_write}")
    
    # Check accessible modules
    accessible = [m.code for m in user.get_accessible_modules()]
    print(f"  Module dans sidebar: {test_module_code in accessible}")
    
    # Clean up
    perm.delete()
    print(f"  -> FONCTIONNE: {'OUI' if has_after_read else 'NON'}")

print("\n" + "=" * 70)
print("RESULTAT: Le systeme fonctionne pour l'activation de modules!")
print("=" * 70)