import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, PermissionUtilisateur

prof = User.objects.filter(role='professeur').first()
print('PermissionUtilisateur avec est_actif=False pour prof:')
for p in PermissionUtilisateur.objects.filter(utilisateur=prof, est_actif=False):
    print(f'  {p.module.code}: actions={p.actions}')

print(f'\nhas_module_permission(bulletins, read): {prof.has_module_permission("bulletins", "read")}')
print(f'Accessible modules: {[m.code for m in prof.get_accessible_modules()]}')
