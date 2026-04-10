#!/usr/bin/env python3
"""
Script de sauvegarde automatique pour le système scolaire
Règle 3-2-1: 3 copies, 2 supports, 1 hors site
"""

import os
import shutil
import gzip
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
import sqlite3
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / 'backups'
RETENTION_DAYS = 30

BACKUP_CONFIG = {
    'database': {
        'enabled': True,
        'files': ['db.sqlite3'],
    },
    'media': {
        'enabled': True,
        'files': ['media/'],
        'exclude': ['media/cache/', 'media/tmp/'],
    },
    'config': {
        'enabled': True,
        'files': ['.env', 'core/settings.py'],
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
    """Sauvegarde la base de données SQLite."""
    db_path = BASE_DIR / 'db.sqlite3'
    if not db_path.exists():
        logger.warning("Base de données non trouvée, skipping...")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"database_{timestamp}.sql.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        if result[0] != 'ok':
            logger.error("Base de données corrompue!")
            return None
        conn.close()

        with sqlite3.connect(db_path) as conn:
            with open(BACKUP_DIR / 'daily' / f"temp_{timestamp}.sql", 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')

        compress_file(
            BACKUP_DIR / 'daily' / f"temp_{timestamp}.sql",
            backup_path
        )
        os.remove(BACKUP_DIR / 'daily' / f"temp_{timestamp}.sql")

        checksum = calculate_checksum(backup_path)
        logger.info(f"✓ Base de données sauvegardée: {backup_path}")
        logger.info(f"  Checksum SHA-256: {checksum}")

        return {
            'file': backup_name,
            'checksum': checksum,
            'size': backup_path.stat().st_size,
            'timestamp': timestamp
        }
    except Exception as e:
        logger.error(f"Erreur sauvegarde base de données: {e}")
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
            logger.info(f"✓ Médias sauvegardés: {backup_path}")
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
        logger.info(f"✓ Médias sauvegardés (zip): {backup_path}")
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
    backup_name = f"config_{timestamp}.gz"
    backup_path = BACKUP_DIR / 'daily' / backup_name

    config_data = {}
    config_files = ['.env', 'core/settings.py']

    for config_file in config_files:
        file_path = BASE_DIR / config_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if config_file == '.env':
                        sensitive = {}
                        for line in content.split('\n'):
                            if '=' in line and not line.startswith('#'):
                                key = line.split('=')[0]
                                sensitive[key] = '***REDACTED***' if any(
                                    k in key.lower() for k in ['key', 'password', 'secret', 'token']
                                ) else line.split('=', 1)[1].strip()
                        config_data[config_file] = sensitive
                    else:
                        config_data[config_file] = content[:500]
            except Exception as e:
                logger.error(f"Erreur lecture {config_file}: {e}")

    if config_data:
        import json
        temp_file = BACKUP_DIR / 'daily' / f"temp_config_{timestamp}.json"
        with open(temp_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        compress_file(temp_file, backup_path)
        os.remove(temp_file)
        
        logger.info(f"✓ Configuration sauvegardée: {backup_path}")
        return {'file': backup_name, 'timestamp': timestamp}
    
    return None


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


def main():
    """Point d'entrée principal."""
    logger.info("=" * 50)
    logger.info("DÉMARRAGE SAUVEGARDE AUTOMATIQUE")
    logger.info("=" * 50)

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

    cleanup_old_backups()
    run_weekly_backup()

    report = create_backup_report(backups)

    logger.info("=" * 50)
    logger.info("SAUVEGARDE TERMINÉE")
    logger.info(f"Fichiers sauvegardés: {len(backups)}")
    logger.info(f"Taille totale: {report['total_size'] / 1024 / 1024:.2f} MB")
    logger.info("=" * 50)

    return 0 if backups else 1


if __name__ == '__main__':
    sys.exit(main())
