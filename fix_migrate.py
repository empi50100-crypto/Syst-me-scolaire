#!/usr/bin/env python
"""
Script pour résoudre le problème de migration contenttypes
"""
import subprocess
import sys

def run_command(cmd):
    """Exécute une commande et affiche le résultat"""
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}", file=sys.stderr)
    return result.returncode == 0

def main():
    # 1. Réinitialiser la base
    print("=== ÉTAPE 1: Réinitialisation de la base ===")
    if not run_command([sys.executable, 'reset_db.py']):
        print("✗ Échec de la réinitialisation")
        return False
    
    # 2. Appliquer contenttypes.0001_initial seul
    print("\n=== ÉTAPE 2: Migration contenttypes.0001 ===")
    if not run_command([sys.executable, 'manage.py', 'migrate', 'contenttypes', '0001_initial']):
        print("✗ Échec de contenttypes.0001_initial")
        return False
    
    # 3. FAKE la migration 0002 (elle essaie de modifier une table qui n'existe pas)
    print("\n=== ÉTAPE 3: Fake migration contenttypes.0002 ===")
    if not run_command([sys.executable, 'manage.py', 'migrate', 'contenttypes', '0002_remove_content_type_name', '--fake']):
        print("✗ Échec du fake de 0002")
        return False
    
    # 4. Appliquer toutes les autres migrations
    print("\n=== ÉTAPE 4: Toutes les autres migrations ===")
    if not run_command([sys.executable, 'manage.py', 'migrate']):
        print("✗ Échec des migrations")
        return False
    
    # 5. Initialiser les modules
    print("\n=== ÉTAPE 5: Initialisation des modules ===")
    if not run_command([sys.executable, 'manage.py', 'init_modules']):
        print("✗ Échec de l'initialisation des modules")
        return False
    
    print("\n" + "="*50)
    print("✓ RÉINITIALISATION COMPLÈTE AVEC SUCCÈS")
    print("="*50)
    return True

if __name__ == '__main__':
    if not main():
        sys.exit(1)
