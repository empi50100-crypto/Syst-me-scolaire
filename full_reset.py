#!/usr/bin/env python
import psycopg2
import subprocess
import sys

try:
    # Connexion à PostgreSQL
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='AMP50100',
        database='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Supprimer la base si elle existe
    cur.execute("DROP DATABASE IF EXISTS gestion_scolaire")
    
    # Recréer la base
    cur.execute("CREATE DATABASE gestion_scolaire")
    
    print('✓ Base de données recréée')
    conn.close()
    
    # Appliquer les migrations Django de base en premier
    print('→ Application des migrations de base...')
    
    # Utiliser subprocess pour appliquer les migrations
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', 'contenttypes'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"contenttypes error: {result.stderr}")
    else:
        print("✓ contenttypes OK")
    
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', 'auth'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"auth error: {result.stderr}")
    else:
        print("✓ auth OK")
    
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', 'admin'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"admin error: {result.stderr}")
    else:
        print("✓ admin OK")
    
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', 'sessions'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"sessions error: {result.stderr}")
    else:
        print("✓ sessions OK")
    
    # Puis toutes les autres migrations
    print('→ Application des migrations des apps...')
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"migrate error: {result.stderr[-500:]}")
        sys.exit(1)
    else:
        print("✓ Toutes les migrations appliquées")
    
    print('\n=== RÉINITIALISATION COMPLÈTE ===')
    
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
