#!/usr/bin/env python
"""
Script de réinitialisation nucléaire - supprime tout et recommence
"""
import psycopg2
import subprocess
import sys

def reset_database():
    """Supprime et recrée la base de données"""
    print("→ Suppression de la base de données...")
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='AMP50100',
        database='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Terminer toutes les connexions
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
    print("✓ Base de données recréée")

def run_migrations():
    """Applique les migrations Django"""
    print("\n→ Application des migrations...")
    
    # D'abord créer les tables système avec migrate
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate'],
        capture_output=True,
        text=True,
        cwd=r'C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole'
    )
    
    if result.returncode != 0:
        print(f"✗ Erreur: {result.stderr[-800:]}")
        return False
    
    print(result.stdout[-500:])
    print("✓ Migrations appliquées")
    return True

def init_modules():
    """Initialise les modules de navigation"""
    print("\n→ Initialisation des modules...")
    result = subprocess.run(
        [sys.executable, 'manage.py', 'init_modules'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✓ Modules initialisés")
        return True
    else:
        print(f"✗ Erreur: {result.stderr}")
        return False

if __name__ == '__main__':
    try:
        reset_database()
        if run_migrations():
            init_modules()
            print("\n" + "="*50)
            print("✓ RÉINITIALISATION COMPLÈTE AVEC SUCCÈS")
            print("="*50)
        else:
            print("\n✗ ÉCHEC DES MIGRATIONS")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        sys.exit(1)
