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
    
    # Créer la table django_content_type manuellement
    cur.execute("""
        CREATE TABLE IF NOT EXISTS django_content_type (
            id SERIAL PRIMARY KEY,
            app_label VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model)
        )
    """)
    
    # Créer la table django_migrations si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS django_migrations (
            id SERIAL PRIMARY KEY,
            app VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            applied TIMESTAMP WITH TIME ZONE NOT NULL
        )
    """)
    
    # Insérer le record pour contenttypes.0001_initial
    cur.execute("""
        INSERT INTO django_migrations (app, name, applied) 
        VALUES ('contenttypes', '0001_initial', NOW())
        ON CONFLICT DO NOTHING
    """)
    
    # Insérer le record pour contenttypes.0002
    cur.execute("""
        INSERT INTO django_migrations (app, name, applied) 
        VALUES ('contenttypes', '0002_remove_content_type_name', NOW())
        ON CONFLICT DO NOTHING
    """)
    
    conn.commit()
    conn.close()
    print("✓ Tables système créées manuellement")
    
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
