import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from enseignement.models importProfesseur
print('Count:',Professeur.objects.count())
list(Professeur.objects.all())
