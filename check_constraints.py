import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection
cursor = connection.cursor()

# Find all constraints on the table
cursor.execute("SELECT constraint_name FROM information_schema.table_constraints WHERE table_name='core_periodeevaluation' AND constraint_type='UNIQUE'")
rows = cursor.fetchall()
for row in rows:
    print('Contrainte trouvée:', row[0])
    
    # Drop each unique constraint
    try:
        cursor.execute(f"ALTER TABLE core_periodeevaluation DROP CONSTRAINT IF EXISTS {row[0]}")
        print(f'  ->Supprimée: {row[0]}')
    except Exception as e:
        print(f'  ->Erreur: {e}')