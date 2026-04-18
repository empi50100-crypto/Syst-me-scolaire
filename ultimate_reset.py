#!/usr/bin/env python
"""
Réinitialisation ultime - gère le problème contenttypes
"""
import psycopg2
import subprocess
import sys

def reset_db():
    """Réinitialise la base de données"""
    print("=== Réinitialisation de la base ===")
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='AMP50100',
        database='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Terminer les connexions
    cur.execute("""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = 'gestion_scolaire' 
        AND pid <> pg_backend_pid()
    """)
    
    # Supprimer et recréer
    cur.execute("DROP DATABASE IF EXISTS gestion_scolaire")
    cur.execute("CREATE DATABASE gestion_scolaire")
    conn.close()
    print("✓ Base réinitialisée")

def makemigrations():
    """Crée toutes les migrations"""
    print("\n=== Création des migrations ===")
    result = subprocess.run(
        [sys.executable, 'manage.py', 'makemigrations'],
        capture_output=True,
        text=True,
        cwd=r'C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole'
    )
    if result.returncode != 0:
        print(f"✗ Erreur: {result.stderr}")
        return False
    print(result.stdout)
    return True

def migrate_contenttypes_only():
    """Migre uniquement contenttypes 0001"""
    print("\n=== Migration contenttypes 0001 ===")
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', 'contenttypes', '0001_initial'],
        capture_output=True,
        text=True,
        cwd=r'C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole'
    )
    if result.returncode != 0:
        print(f"✗ Erreur: {result.stderr[-500:]}")
        return False
    print(result.stdout)
    return True

def fake_contenttypes_0002():
    """Fake la migration contenttypes 0002"""
    print("\n=== Fake contenttypes 0002 ===")
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', 'contenttypes', '0002_remove_content_type_name', '--fake'],
        capture_output=True,
        text=True,
        cwd=r'C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole'
    )
    if result.returncode != 0:
        print(f"✗ Erreur: {result.stderr[-500:]}")
        return False
    print(result.stdout)
    return True

def migrate_all():
    """Migre tout le reste"""
    print("\n=== Migration complète ===")
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate'],
        capture_output=True,
        text=True,
        cwd=r'C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole'
    )
    if result.returncode != 0:
        print(f"✗ Erreur: {result.stderr[-1000:]}")
        return False
    print(result.stdout[-500:])
    return True

def init_modules():
    """Initialise les modules"""
    print("\n=== Initialisation des modules ===")
    result = subprocess.run(
        [sys.executable, 'manage.py', 'init_modules'],
        capture_output=True,
        text=True,
        cwd=r'C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole'
    )
    if result.returncode != 0:
        print(f"✗ Erreur: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    reset_db()
    
    if not makemigrations():
        return False
    
    if not migrate_contenttypes_only():
        return False
    
    if not fake_contenttypes_0002():
        return False
    
    if not migrate_all():
        return False
    
    if not init_modules():
        return False
    
    print("\n" + "="*50)
    print("✓ RÉINITIALISATION COMPLÈTE AVEC SUCCÈS")
    print("="*50)
    return True

if __name__ == '__main__':
    if not main():
        sys.exit(1)
