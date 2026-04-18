#!/usr/bin/env python
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='AMP50100',
        database='gestion_scolaire'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Supprimer toutes les tables
    cur.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    
    print('SUCCESS: Toutes les tables supprimees')
    conn.close()
    
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
