import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, PermissionUtilisateur, Permission

# Clean up: Delete PermissionUtilisateur with est_actif=False that would block role-based permissions
# This fixes the issue where admin disabled a module but user should still have role-based access

print('=== Cleaning up blocking PermissionUtilisateur records ===')
count = 0

for pu in PermissionUtilisateur.objects.filter(est_actif=False):
    # Check if there's a role-based permission that should apply
    role_perm = Permission.objects.filter(role=pu.utilisateur.role, module=pu.module).first()
    
    # If there's a role-based permission with actions, delete the blocking record
    if role_perm and role_perm.actions:
        print(f'Deleting blocking permission: User={pu.utilisateur.username}, Module={pu.module.code}')
        print(f'  Role-based permission exists: {role_perm.actions}')
        pu.delete()
        count += 1

print(f'\nDeleted {count} blocking records')

# Test again
print('\n=== Test after cleanup ===')
for code in ['eleve_list', 'bulletins', 'saisie_notes']:
    result = User.objects.get(username='prof').has_module_permission(code, 'read')
    print(f'prof can read {code}: {result}')