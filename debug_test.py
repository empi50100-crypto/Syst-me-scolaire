from accounts.models import User, PermissionUtilisateur

# Find the actual 'prof' user
prof = User.objects.filter(username='prof').first()
if prof:
    print(f'User: {prof.username}, Role: {prof.role}')
    print(f'is_direction: {prof.is_direction()}, is_superadmin: {prof.is_superadmin()}')
    print()
    print('Testing has_module_permission:')
    for mod in ['eleve_list', 'classe_list', 'bulletins', 'saisie_notes']:
        print(f'  {mod} read: {prof.has_module_permission(mod, "read")}')
        print(f'  {mod} write: {prof.has_module_permission(mod, "write")}')
    print()
    print('Accessible modules (sidebar):', [m.code for m in prof.get_accessible_modules()[:10]])
else:
    print('User prof not found')

# Check what PermissionUtilisateur exists for prof
print()
print('PermissionUtilisateur for prof:')
for pu in PermissionUtilisateur.objects.filter(utilisateur=prof):
    print(f'  Module: {pu.module.code}, est_actif: {pu.est_actif}, actions: {pu.actions}')