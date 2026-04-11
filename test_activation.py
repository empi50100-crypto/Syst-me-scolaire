import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, PermissionUtilisateur, Module

prof = User.objects.filter(role='professeur').first()
module = Module.objects.filter(code='annee_scolaire').first()

print('=== Test: Creation de PermissionUtilisateur pour activer un module ===')
print(f'Professeur: {prof.username}')
print(f'Module: {module.code}')

# Check if permission already exists
existing = PermissionUtilisateur.objects.filter(utilisateur=prof, module=module).first()
print(f'Permission existante: {existing}')

# Create a PermissionUtilisateur as if admin activated it
if not existing:
    perm = PermissionUtilisateur.objects.create(
        utilisateur=prof,
        module=module,
        actions=['read', 'write'],
        niveau='complet',
        est_actif=True
    )
    print(f'Permission creee: {perm}')
    print(f'  est_actif: {perm.est_actif}')
    print(f'  actions: {perm.actions}')
    print(f'  is_valid: {perm.is_valid()}')

# Now test has_module_permission
print(f'\n--- Test apres creation ---')
print(f'has_module_permission(annee_scolaire, read): {prof.has_module_permission("annee_scolaire", "read")}')
print(f'has_module_permission(annee_scolaire, write): {prof.has_module_permission("annee_scolaire", "write")}')
print(f'has_module_permission(annee_scolaire, delete): {prof.has_module_permission("annee_scolaire", "delete")}')

# Check accessible modules
accessible = prof.get_accessible_modules()
print(f'\nAccessible modules: {accessible.count()}')
print(f'annee_scolaire in accessible: {"annee_scolaire" in [m.code for m in accessible]}')
