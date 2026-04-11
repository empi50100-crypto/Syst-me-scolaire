import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from enseignement.models importProfesseur
print('Total professors:',Professeur.objects.count())
print('Available PKs:', list(Professeur.objects.values_list('pk', flat=True)))
