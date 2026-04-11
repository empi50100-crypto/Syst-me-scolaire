import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import Module, Permission

print('=' * 70)
print('TOUS LES MODULES ET LEURS PERMISSIONS PAR ROLE')
print('=' * 70)

modules = Module.objects.all()
roles = ['superadmin', 'direction', 'secretaire', 'comptable', 'professeur', 'surveillance']

for m in modules:
    print(f'\n--- {m.code} ({m.nom}) ---')
    for r in roles:
        p = Permission.objects.filter(role=r, module=m).first()
        if p and p.actions:
            print(f'  {r}: {p.actions}')
        elif not p:
            pass  # Skip None permissions

print('\n' + '=' * 70)
print('ROLES SANS PERMISSIONS POUR CERTAINS MODULES')
print('=' * 70)

for r in roles:
    perms_count = Permission.objects.filter(role=r).count()
    total_modules = Module.objects.count()
    missing = total_modules - perms_count
    print(f'{r}: {perms_count}/{total_modules} modules')
    if missing > 0:
        print(f'  -> {missing} modules non définis')
