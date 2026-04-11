import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection
cursor = connection.cursor()

# Check for indexes on the table
cursor.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename='core_periodeevaluation'")
rows = cursor.fetchall()
print("Indexes sur core_periodeevaluation:")
for row in rows:
    print(f"  {row[0]}: {row[1]}")
    
    # Drop unique indexes (not primary key)
    if 'unique' in row[1].lower() and 'pri' not in row[0].lower():
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {row[0]}")
            print(f"    ->Supprimé: {row[0]}")
        except Exception as e:
            print(f"    ->Erreur: {e}")