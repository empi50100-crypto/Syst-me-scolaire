import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, PermissionUtilisateur, Permission

prof = User.objects.filter(username='prof').first()
print('Role:', prof.role)
print()

print('PermissionUtilisateur for prof:')
for pu in PermissionUtilisateur.objects.filter(utilisateur=prof):
    print(f'  {pu.module.code}: active={pu.est_actif}, actions={pu.actions}, valid={pu.is_valid()}')

print()
print('Checking eleve_list permission:')
# Check PermissionUtilisateur
p = PermissionUtilisateur.objects.filter(utilisateur=prof, module__code='eleve_list', est_actif=True).first()
print(f'PermissionUtilisateur (active): {p}')

# Check Permission (role-based)
role_perm = Permission.objects.filter(role=prof.role, module__code='eleve_list').first()
print(f'Permission (role-based): {role_perm}')

# Test has_module_permission
print()
print('Test has_module_permission:')
print(f'  eleve_list read: {prof.has_module_permission("eleve_list", "read")}')
