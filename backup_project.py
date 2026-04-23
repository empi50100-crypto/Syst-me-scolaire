#!/usr/bin/env python
"""
Script de sauvegarde du projet SyGeS-AM
Crée une archive ZIP avec la date et l'heure
"""

import os
import zipfile
from datetime import datetime
import shutil

def backup_project():
    """Crée une sauvegarde du projet"""
    
    # Répertoire du projet
    project_dir = r"c:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole"
    
    # Créer le dossier de sauvegarde s'il n'existe pas
    backup_dir = os.path.join(project_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Nom de l'archive avec date et heure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"SyGeS_AM_backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Extensions et dossiers à exclure
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe'}
    exclude_dirs = {
        '__pycache__', '.git', 'venv', 'env', '.venv', 
        'node_modules', '.pytest_cache', '.mypy_cache',
        'backups', 'media', 'staticfiles', '.windsurf'
    }
    exclude_files = {
        'db.sqlite3', '*.pyc', '*.pyo', '.env', '.env.local'
    }
    
    print(f"Création de la sauvegarde: {backup_name}")
    print("Exclusion des fichiers temporaires et caches...")
    
    file_count = 0
    excluded_count = 0
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Filtrer les dossiers à exclure
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Vérifier les extensions exclues
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_extensions:
                    excluded_count += 1
                    continue
                
                # Vérifier les fichiers exclus
                if file in exclude_files or file.endswith(('.pyc', '.pyo')):
                    excluded_count += 1
                    continue
                
                # Ne pas inclure les fichiers de sauvegarde existants
                if 'backup_' in file and file.endswith('.zip'):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                
                try:
                    zipf.write(file_path, arcname)
                    file_count += 1
                    
                    # Afficher la progression tous les 100 fichiers
                    if file_count % 100 == 0:
                        print(f"  ... {file_count} fichiers archivés")
                        
                except Exception as e:
                    print(f"  ⚠ Erreur avec {arcname}: {e}")
    
    # Obtenir la taille du fichier
    size_bytes = os.path.getsize(backup_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print(f"\n✅ Sauvegarde créée avec succès!")
    print(f"📁 Fichier: {backup_path}")
    print(f"📊 Taille: {size_mb:.2f} Mo")
    print(f"📄 Fichiers sauvegardés: {file_count}")
    print(f"🗑️ Fichiers exclus: {excluded_count}")
    
    # Nettoyer les anciennes sauvegardes (garder les 5 dernières)
    cleanup_old_backups(backup_dir, keep=5)
    
    return backup_path

def cleanup_old_backups(backup_dir, keep=5):
    """Nettoie les anciennes sauvegardes, garde uniquement les 'keep' plus récentes"""
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('SyGeS_AM_backup_') and f.endswith('.zip')]
    
    if len(backups) > keep:
        # Trier par date (le nom contient la date)
        backups.sort(reverse=True)
        
        # Supprimer les anciennes
        for old_backup in backups[keep:]:
            old_path = os.path.join(backup_dir, old_backup)
            try:
                os.remove(old_path)
                print(f"🗑️ Ancienne sauvegarde supprimée: {old_backup}")
            except Exception as e:
                print(f"⚠ Impossible de supprimer {old_backup}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("  SAUVEGARDE DU PROJET SyGeS-AM")
    print("=" * 60)
    print()
    
    backup_file = backup_project()
    
    print()
    print("=" * 60)
    print("  SAUVEGARDE TERMINÉE")
    print("=" * 60)
