import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import Module

print('=== Module URLs ===')
for m in Module.objects.all():
    print(f'{m.code}: {m.url}')