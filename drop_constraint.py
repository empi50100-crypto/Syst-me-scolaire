import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection
cursor = connection.cursor()

# Check ALL constraints on this table
cursor.execute("""
    SELECT conname, contype 
    FROM pg_constraint 
    WHERE conrelid = 'core_periodeevaluation'::regclass
""")
rows = cursor.fetchall()
print("Toutes les contraintes sur core_periodeevaluation:")
for row in rows:
    print(f"  {row[0]} (type: {row[1]})")
    
    # Drop unique constraints ('u' = unique, 'p' = primary key)
    if row[1] == 'u':
        try:
            cursor.execute(f"ALTER TABLE core_periodeevaluation DROP CONSTRAINT IF EXISTS {row[0]}")
            print(f"    ->Supprimée!")
        except Exception as e:
            print(f"    ->Erreur: {e}")