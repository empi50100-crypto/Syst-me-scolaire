"""Vérifier les permissions du secrétariat"""
import os
import sys
import django

sys.path.insert(0, r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Module, Permission, PermissionUtilisateur

sec = User.objects.get(username='secretariat')
print(f'Utilisateur: {sec.username}')
print(f'Rôle: {sec.role}')
print(f'is_superadmin: {sec.is_superadmin()}')
print(f'is_direction: {sec.is_direction()}')

print()
print('=== Permission de RÔLE pour Secrétariat ===')
perms = Permission.objects.filter(role='secretaire')
for p in perms:
    print(f'  {p.module.code}: {p.actions}')

print()
print('=== PermissionUtilisateur personnalisées ===')
user_perms = PermissionUtilisateur.objects.filter(utilisateur=sec)
for p in user_perms:
    print(f'  {p.module.code}: est_actif={p.est_actif}, actions={p.actions}, is_valid={p.is_valid()}')

print()
print('=== Test discipline ===')
result = sec.has_module_permission('discipline', 'read')
print(f'has_module_permission(discipline, read): {result}')

print()
print('=== Tous les modules accessibles avec read ===')
for mod in Module.objects.all():
    read = sec.has_module_permission(mod.code, 'read')
    write = sec.has_module_permission(mod.code, 'write')
    if read or write:
        print(f'  {mod.code}: read={read}, write={write}')
