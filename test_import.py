import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

# Try to import the form
try:
    from academics.forms importProfesseurForm
    print("Import OK")
except ImportError as e:
    print(f"ImportError: {e}")
except SyntaxError as e:
    print(f"SyntaxError: {e}")