import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

import enseignement.models as models_module
Professeur = getattr(models_module, 'Professeur')
print('Type:', type(Professeur))
print('Count:',Professeur.objects.count())
for p inProfesseur.objects.all():
    print('PK:', p.pk)
