import os
import sys
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

result = subprocess.run(
    [sys.executable, '-c', 
     'import django; django.setup(); print("Setup OK")'],
    cwd='C:/Users/empi5/Desktop/Système scolaire/gestion_ecole',
    capture_output=True,
    text=True
)
print('Result:', result.returncode)
print('stdout:', result.stdout)
print('stderr:', result.stderr[:500] if result.stderr else '')