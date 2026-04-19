#!/usr/bin/env python3
"""
Script de sauvegarde automatique pour le système scolaire SyGeS-AM
Règle 3-2-1: 3 copies, 2 supports, 1 hors site
Compatible PostgreSQL et SQLite
"""

import os
import shutil
import gzip
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import subprocess
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).resolve().parent.parent / 'logs' / 'backup.log')
    ]
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / 'backups'
RETENTION_DAYS = 30

# Charger les variables d'environnement si disponibles
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Variables d'environnement chargées depuis {env_path}")
except ImportError:
    logger.warning("python-dotenv non installé, utilisation des variables système")

BACKUP_CONFIG = {
    'database': {
        'enabled': True,
        'type': os.getenv('DB_ENGINE', 'postgresql'),  # postgresql ou sqlite
    },
    'media': {
        'enabled': True,
        'files': ['media/'],
        'exclude': ['media/cache/', 'media/tmp/'],
    },
    'config': {
        'enabled': True,
        'files': ['.env', 'core/settings.py', '.env.example'],
    },
    'documents': {
        'enabled': True,
        'files': ['GUIDE_*.md', 'MANUEL_*.md', 'README.md', 'ARCHITECTURE.md'],
    },
}


def ensure_backup_dir():
    """Crée le répertoire de sauvegarde s'il n'existe pas."""
    for subdir in ['daily', 'weekly', 'monthly', 'encrypted']:
        dir_path = BACKUP_DIR / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Répertoires de sauvegarde créés/vérifiés dans {BACKUP_DIR}")


def calculate_checksum(file_path):
    """Calcule le hash SHA-256 d'un fichier."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Erreur calcul checksum {file_path}: {e}")
        return None


def compress_file(source_path, dest_path):
    """Compresse un fichier avec gzip."""
    try:
        with open(source_path, 'rb') as f_in:
            with gzip.open(dest_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return True
    except Exception as e:
        logger.error(f"Erreur compression {source_path}: {e}")
        return False


def backup_database():
    """Sauvegarde la base de données (PostgreSQL ou SQLite)."""
    db_type = BACKUP_CONFIG['database']['type']
    
    if db_type == 'postgresql':
        return backup_postgresql()
    else:
        return backup_sqlite()


def backup_postgresql():
    """Sauvegarde la base de données PostgreSQL."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"database_postgresql_{timestamp}.sql.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name
    
    # Récupérer les credentials depuis les variables d'environnement
    db_name = os.getenv('DB_NAME', 'gestion_scolaire')
    db_user = os.getenv('DB_USER', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    # Pour la sécurité, ne pas logger le mot de passe
    db_password = os.getenv('DB_PASSWORD', '')
    
    if not db_password:
        logger.error("DB_PASSWORD non défini. Impossible de sauvegarder PostgreSQL.")
        logger.info("Solution: Définir DB_PASSWORD dans le fichier .env")
        return None
    
    try:
        # Utiliser pg_dump avec mot de passe via variable d'environnement
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        pg_dump_path = 'pg_dump'
        
        # Commande pg_dump avec options
        cmd = [
            pg_dump_path,
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '--clean',  # Inclure les commandes DROP
            '--if-exists',  # Utiliser IF EXISTS
            '--verbose'
        ]
        
        logger.info(f"Sauvegarde PostgreSQL: {db_name}@{db_host}:{db_port}")
        
        # Exécuter pg_dump et compresser directement
        with gzip.open(backup_path, 'wb') as f_out:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            if result.returncode == 0:
                f_out.write(result.stdout)
            else:
                logger.error(f"pg_dump erreur: {result.stderr.decode()}")
                return None
        
        checksum = calculate_checksum(backup_path)
        size_mb = backup_path.stat().st_size / 1024 / 1024
        
        logger.info(f"[OK] Base PostgreSQL sauvegardée: {backup_path}")
        logger.info(f"  Taille: {size_mb:.2f} MB")
        logger.info(f"  Checksum SHA-256: {checksum}")
        
        return {
            'file': backup_name,
            'checksum': checksum,
            'size': backup_path.stat().st_size,
            'timestamp': timestamp,
            'type': 'postgresql'
        }
        
    except FileNotFoundError:
        logger.error("pg_dump non trouvé. Installez PostgreSQL client tools.")
        logger.info("Téléchargement: https://www.postgresql.org/download/")
        return None
    except Exception as e:
        logger.error(f"Erreur sauvegarde PostgreSQL: {e}")
        return None


def backup_sqlite():
    """Sauvegarde la base de données SQLite (legacy)."""
    db_path = BASE_DIR / 'db.sqlite3'
    if not db_path.exists():
        logger.warning("Base de données SQLite non trouvée, skipping...")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"database_sqlite_{timestamp}.sql.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name

    try:
        # Vérifier l'intégrité
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        if result[0] != 'ok':
            logger.error("Base de données SQLite corrompue!")
            return None
        conn.close()

        # Dump et compression
        temp_sql = BACKUP_DIR / 'daily' / f"temp_{timestamp}.sql"
        with sqlite3.connect(db_path) as conn:
            with open(temp_sql, 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')

        compress_file(temp_sql, backup_path)
        os.remove(temp_sql)

        checksum = calculate_checksum(backup_path)
        logger.info(f"[OK] Base SQLite sauvegardée: {backup_path}")
        logger.info(f"  Checksum SHA-256: {checksum}")

        return {
            'file': backup_name,
            'checksum': checksum,
            'size': backup_path.stat().st_size,
            'timestamp': timestamp,
            'type': 'sqlite'
        }
    except Exception as e:
        logger.error(f"Erreur sauvegarde SQLite: {e}")
        return None


def backup_media():
    """Sauvegarde les fichiers médias."""
    media_path = BASE_DIR / 'media'
    if not media_path.exists():
        logger.warning("Répertoire media non trouvé, skipping...")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"media_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name

    try:
        result = subprocess.run(
            ['tar', '-czf', str(backup_path), '-C', str(BASE_DIR), 'media'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            checksum = calculate_checksum(backup_path)
            logger.info(f"[OK] Médias sauvegardés: {backup_path}")
            logger.info(f"  Taille: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
            logger.info(f"  Checksum SHA-256: {checksum}")
            return {
                'file': backup_name,
                'checksum': checksum,
                'size': backup_path.stat().st_size,
                'timestamp': timestamp
            }
        else:
            logger.error(f"Erreur tar: {result.stderr}")
            return None
    except FileNotFoundError:
        logger.warning("tar non disponible, copie simple des médias...")
        return simple_media_backup(timestamp)
    except Exception as e:
        logger.error(f"Erreur sauvegarde médias: {e}")
        return None


def simple_media_backup(timestamp):
    """Backup simple sans tar."""
    media_path = BASE_DIR / 'media'
    backup_name = f"media_{timestamp}.zip"
    backup_path = BACKUP_DIR / 'daily' / backup_name
    
    try:
        shutil.make_archive(
            str(backup_path.with_suffix('')),
            'zip',
            media_path
        )
        checksum = calculate_checksum(backup_path)
        logger.info(f"[OK] Médias sauvegardés (zip): {backup_path}")
        return {
            'file': backup_name,
            'checksum': checksum,
            'size': backup_path.stat().st_size,
            'timestamp': timestamp
        }
    except Exception as e:
        logger.error(f"Erreur backup zip: {e}")
        return None


def backup_config():
    """Sauvegarde les fichiers de configuration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"config_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name

    config_files = ['.env.example', 'core/settings.py', 'requirements.txt']
    temp_dir = BACKUP_DIR / 'daily' / f"temp_config_{timestamp}"
    temp_dir.mkdir(exist_ok=True)

    try:
        for config_file in config_files:
            file_path = BASE_DIR / config_file
            if file_path.exists():
                if file_path.is_file():
                    shutil.copy2(file_path, temp_dir / file_path.name)
                elif file_path.is_dir():
                    shutil.copytree(file_path, temp_dir / file_path.name)

        # Créer une archive tar.gz
        result = subprocess.run(
            ['tar', '-czf', str(backup_path), '-C', str(temp_dir), '.'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            checksum = calculate_checksum(backup_path)
            logger.info(f"[OK] Configuration sauvegardée: {backup_path}")
            return {
                'file': backup_name,
                'checksum': checksum,
                'size': backup_path.stat().st_size,
                'timestamp': timestamp
            }
        else:
            logger.error(f"Erreur tar config: {result.stderr}")
            return None

    except Exception as e:
        logger.error(f"Erreur sauvegarde config: {e}")
        return None
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def backup_documents():
    """Sauvegarde les documents (guides, manuels, README)."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"documents_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name

    doc_patterns = ['GUIDE_*.md', 'MANUEL_*.md', 'README.md', 'ARCHITECTURE.md', 
                    'DEPLOYMENT_SECURITY_CHECKLIST.md', 'SOLUTION_IMPORT_CIRCULAIRE.md']
    
    temp_dir = BACKUP_DIR / 'daily' / f"temp_docs_{timestamp}"
    temp_dir.mkdir(exist_ok=True)

    try:
        found_files = False
        for pattern in doc_patterns:
            for file_path in BASE_DIR.glob(pattern):
                if file_path.is_file():
                    shutil.copy2(file_path, temp_dir / file_path.name)
                    found_files = True

        if not found_files:
            logger.warning("Aucun document trouvé à sauvegarder")
            return None

        # Créer l'archive
        result = subprocess.run(
            ['tar', '-czf', str(backup_path), '-C', str(temp_dir), '.'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            checksum = calculate_checksum(backup_path)
            size_mb = backup_path.stat().st_size / 1024 / 1024
            logger.info(f"[OK] Documents sauvegardés: {backup_path}")
            logger.info(f"  Taille: {size_mb:.2f} MB")
            return {
                'file': backup_name,
                'checksum': checksum,
                'size': backup_path.stat().st_size,
                'timestamp': timestamp
            }
        else:
            logger.error(f"Erreur tar documents: {result.stderr}")
            return None

    except FileNotFoundError:
        # Fallback sans tar
        backup_name_zip = f"documents_{timestamp}.zip"
        backup_path_zip = BACKUP_DIR / 'daily' / backup_name_zip
        shutil.make_archive(str(backup_path_zip.with_suffix('')), 'zip', temp_dir)
        checksum = calculate_checksum(backup_path_zip)
        logger.info(f"[OK] Documents sauvegardés (zip): {backup_path_zip}")
        return {
            'file': backup_name_zip,
            'checksum': checksum,
            'size': backup_path_zip.stat().st_size,
            'timestamp': timestamp
        }
    except Exception as e:
        logger.error(f"Erreur sauvegarde documents: {e}")
        return None
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def cleanup_old_backups():
    """Supprime les anciennes sauvegardes selon la politique de rétention."""
    cutoff = datetime.now().timestamp() - (RETENTION_DAYS * 24 * 60 * 60)
    
    for subdir in ['daily', 'weekly', 'monthly']:
        dir_path = BACKUP_DIR / subdir
        if dir_path.exists():
            for backup_file in dir_path.glob('*'):
                if backup_file.stat().st_mtime < cutoff:
                    backup_file.unlink()
                    logger.info(f"Supprimé (rétention): {backup_file.name}")


def create_backup_report(backups):
    """Crée un rapport de sauvegarde."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report = {
        'backup_date': timestamp,
        'backups': backups,
        'total_size': sum(b.get('size', 0) for b in backups if b),
        'retention_days': RETENTION_DAYS
    }

    report_path = BACKUP_DIR / 'backup_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Rapport de sauvegarde: {report_path}")
    return report


def verify_backup(backup_path):
    """Vérifie l'intégrité d'une sauvegarde."""
    if not backup_path.exists():
        return False
    
    try:
        if backup_path.suffix == '.gz':
            import gzip
            with gzip.open(backup_path, 'rb') as f:
                f.read(1024)
        return True
    except Exception as e:
        logger.error(f"Sauvegarde corrompue: {e}")
        return False


def run_weekly_backup():
    """Déplace les sauvegardes quotidiennes importantes en weekly."""
    daily_dir = BACKUP_DIR / 'daily'
    weekly_dir = BACKUP_DIR / 'weekly'
    
    if daily_dir.exists():
        for db_backup in daily_dir.glob('database_*.gz'):
            if datetime.fromtimestamp(db_backup.stat().st_mtime).weekday() == 0:
                shutil.copy2(db_backup, weekly_dir / db_backup.name)
                logger.info(f"Weekly backup: {db_backup.name}")


def restore_database(backup_file_path):
    """Restaure la base de données depuis une sauvegarde."""
    db_type = BACKUP_CONFIG['database']['type']
    backup_path = Path(backup_file_path)
    
    if not backup_path.exists():
        logger.error(f"Fichier de sauvegarde non trouvé: {backup_path}")
        return False
    
    logger.warning("⚠️ CETTE OPÉRATION ÉCRASERA LES DONNÉES ACTUELLES!")
    logger.info(f"Restauration depuis: {backup_path}")
    
    if db_type == 'postgresql':
        return restore_postgresql(backup_path)
    else:
        return restore_sqlite(backup_path)


def restore_postgresql(backup_path):
    """Restaure une base PostgreSQL depuis une sauvegarde .sql.gz"""
    db_name = os.getenv('DB_NAME', 'gestion_scolaire')
    db_user = os.getenv('DB_USER', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_password = os.getenv('DB_PASSWORD', '')
    
    if not db_password:
        logger.error("DB_PASSWORD non défini")
        return False
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        # Décompresser et restaurer
        import gzip
        with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Utiliser psql pour restaurer
        cmd = [
            'psql',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-f', '-'  # Lire depuis stdin
        ]
        
        result = subprocess.run(
            cmd,
            input=sql_content,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"[OK] Base PostgreSQL restaurée depuis {backup_path}")
            return True
        else:
            logger.error(f"Erreur psql: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur restauration PostgreSQL: {e}")
        return False


def restore_sqlite(backup_path):
    """Restaure une base SQLite depuis une sauvegarde .sql.gz"""
    db_path = BASE_DIR / 'db.sqlite3'
    
    try:
        # Backup de la base actuelle
        if db_path.exists():
            backup_current = BASE_DIR / f'db.sqlite3.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            shutil.copy2(db_path, backup_current)
            logger.info(f"Base actuelle sauvegardée: {backup_current}")
        
        # Décompresser
        import gzip
        with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Recréer la base
        if db_path.exists():
            db_path.unlink()
        
        with sqlite3.connect(db_path) as conn:
            conn.executescript(sql_content)
        
        logger.info(f"[OK] Base SQLite restaurée depuis {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur restauration SQLite: {e}")
        return False


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sauvegarde du Système Scolaire SyGeS-AM')
    parser.add_argument('--restore', help='Restaurer depuis un fichier de sauvegarde')
    parser.add_argument('--list', action='store_true', help='Lister les sauvegardes disponibles')
    parser.add_argument('--db-type', choices=['postgresql', 'sqlite'], 
                        help='Type de base de données (défaut: postgresql)')
    
    args = parser.parse_args()
    
    if args.restore:
        return 0 if restore_database(args.restore) else 1
    
    if args.list:
        list_backups()
        return 0
    
    if args.db_type:
        BACKUP_CONFIG['database']['type'] = args.db_type
    
    # Sauvegarde normale
    logger.info("=" * 60)
    logger.info("DÉMARRAGE SAUVEGARDE AUTOMATIQUE - SyGeS-AM")
    logger.info(f"Type de base: {BACKUP_CONFIG['database']['type']}")
    logger.info("=" * 60)

    ensure_backup_dir()

    backups = []

    if BACKUP_CONFIG['database']['enabled']:
        db_backup = backup_database()
        if db_backup:
            backups.append(db_backup)

    if BACKUP_CONFIG['media']['enabled']:
        media_backup = backup_media()
        if media_backup:
            backups.append(media_backup)

    if BACKUP_CONFIG['config']['enabled']:
        config_backup = backup_config()
        if config_backup:
            backups.append(config_backup)
            
    if BACKUP_CONFIG['documents']['enabled']:
        docs_backup = backup_documents()
        if docs_backup:
            backups.append(docs_backup)

    cleanup_old_backups()
    run_weekly_backup()

    report = create_backup_report(backups)

    logger.info("=" * 60)
    logger.info("SAUVEGARDE TERMINÉE")
    logger.info(f"Fichiers sauvegardés: {len(backups)}")
    logger.info(f"Taille totale: {report['total_size'] / 1024 / 1024:.2f} MB")
    logger.info(f"Emplacement: {BACKUP_DIR}")
    logger.info("=" * 60)

    return 0 if backups else 1


def list_backups():
    """Liste les sauvegardes disponibles."""
    logger.info("Sauvegardes disponibles:")
    for subdir in ['daily', 'weekly', 'monthly']:
        dir_path = BACKUP_DIR / subdir
        if dir_path.exists():
            logger.info(f"\n{subdir.upper()}:")
            backups = sorted(dir_path.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)
            for backup in backups[:10]:  # 10 dernières
                size_mb = backup.stat().st_size / 1024 / 1024
                date = datetime.fromtimestamp(backup.stat().st_mtime)
                logger.info(f"  {backup.name} ({size_mb:.2f} MB) - {date.strftime('%Y-%m-%d %H:%M')}")


if __name__ == '__main__':
    sys.exit(main())
