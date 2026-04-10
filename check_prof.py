import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from academics.models import Professeur
print('PKs:', list(Professeur.objects.values_list('pk', flat=True)))
print('With user:', list(Professeur.objects.values_list('pk', 'user_id')))