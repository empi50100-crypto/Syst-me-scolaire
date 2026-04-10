import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, PermissionUtilisateur, Module

# Simulate what happens when admin activates a module
print('=== Test: Admin active un module pour un utilisateur ===')

# Get a professor
prof = User.objects.filter(role='professeur').first()
print(f'Professeur: {prof.username}')

# Check which modules are NOT in accessible (shouldn't appear in sidebar)
accessible_codes = [m.code for m in prof.get_accessible_modules()]
all_modules = Module.objects.all()

print(f'\nModules NON accessibles pour professeur ({len(accessible_codes)}/{all_modules.count()}):')
for m in all_modules:
    if m.code not in accessible_codes:
        print(f'  {m.code} - {m.nom}')

# Now simulate what happens if admin adds PermissionUtilisateur for a module
# that the professor doesn't have by default
test_module = Module.objects.filter(code='annee_scolaire').first()
print(f'\n--- Simulation: Admin ajoute permission pour {test_module.code} ---')

# Check if permission already exists
existing = PermissionUtilisateur.objects.filter(utilisateur=prof, module=test_module).first()
print(f'Permission existante: {existing}')

# Test has_module_permission
print(f'has_module_permission(annee_scolaire, read): {prof.has_module_permission("annee_scolaire", "read")}')

# Now let's check: if admin creates a PermissionUtilisateur, will it work?
print(f'\n--- Verifier la logique: ---')
print('1. Admin cree PermissionUtilisateur avec est_actif=True')
print('2. has_module_permission doit retourner True')
print('3. La vue doit autoriser l\'acces')

# Check current logic
perm_user = PermissionUtilisateur.objects.filter(
    utilisateur=prof,
    module__code='annee_scolaire',
    est_actif=True
).first()
print(f'4. PermissionUtilisateur trouvee: {perm_user}')

# Check role-based permission
from accounts.models import Permission
role_perm = Permission.objects.filter(role='professeur', module__code='annee_scolaire').first()
print(f'5. Permission de role: {role_perm}')