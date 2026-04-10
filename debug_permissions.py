import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import PermissionUtilisateur

print('=== All PermissionUtilisateur records ===')
for p in PermissionUtilisateur.objects.all():
    actions = p.actions or []
    print(f'{p.utilisateur.username} - {p.module.code}:')
    print(f'  actions={actions}, active={p.est_actif}, valid={p.is_valid()}')