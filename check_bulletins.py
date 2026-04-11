import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import Permission

# Check permissions for each role for bulletins
for role in ['professeur', 'secretaire', 'comptable', 'surveillance']:
    p = Permission.objects.filter(role=role, module__code='bulletins').first()
    print(f"{role}: {p.actions if p else 'None'}")
