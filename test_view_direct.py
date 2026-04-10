import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User
from django.test import RequestFactory
from eleves import views as eleve_views

# Create a test request
factory = RequestFactory()
request = factory.get('/eleves/')

# Add user to request
sec = User.objects.filter(role='secretaire').first()
request.user = sec

# Try to call the view directly
try:
    response = eleve_views.eleve_list(request)
    print(f'Response status: {response.status_code}')
    print(f'Response type: {type(response)}')
    
    # Check if it's a redirect
    if hasattr(response, 'url'):
        print(f'Redirects to: {response.url}')
    elif hasattr(response, 'content'):
        content = response.content.decode('utf-8')
        if len(content) < 100:
            print(f'Content: {content}')
        else:
            print(f'Content length: {len(content)} chars')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')