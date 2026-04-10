import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123',
        first_name='Admin',
        last_name='System',
        role='direction'
    )
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
