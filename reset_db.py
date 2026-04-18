#!/usr/bin/env python
import psycopg2

try:
    # Connexion à la base 'postgres' pour gérer les autres bases
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='AMP50100',
        database='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Terminer les connexions actives sur gestion_scolaire
    cur.execute("""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = 'gestion_scolaire' 
        AND pid <> pg_backend_pid()
    """)
    
    # Supprimer la base si elle existe
    cur.execute('DROP DATABASE IF EXISTS gestion_scolaire')
    
    # Recréer la base
    cur.execute('CREATE DATABASE gestion_scolaire')
    
    print('SUCCESS: Base de donnees reinitialisee avec succes')
    conn.close()
    
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
