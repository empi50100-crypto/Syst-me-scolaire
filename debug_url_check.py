import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, Module

# Get a non-admin user
user = User.objects.filter(role='secretaire').first()
print(f'User: {user.username} ({user.role})')

# Get accessible modules
accessible = user.get_accessible_modules()
print(f'\nAccessible modules: {accessible.count()}')

# Check each module URL
print('\nChecking module URLs:')
errors = []
for m in accessible:
    # Try to resolve URL
    from django.urls import resolve, Resolver404
    try:
        match = resolve(m.url)
        print(f'  {m.code}: OK ({match.func.__name__})')
    except Resolver404:
        print(f'  {m.code}: 404 NOT FOUND - {m.url}')
        errors.append(m.code)
    except Exception as e:
        print(f'  {m.code}: ERROR - {e}')
        errors.append(m.code)

if errors:
    print(f'\nERRORS FOUND: {errors}')
else:
    print('\nAll module URLs are valid!')