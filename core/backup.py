import os
import shutil
import gzip
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """Gestionnaire de sauvegardes automatiques"""
    
    def __init__(self, backup_dir=None):
        self.backup_dir = backup_dir or getattr(settings, 'BACKUP_DIR', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_backup_filename(self, prefix='backup'):
        """Génère un nom de fichier de sauvegarde"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}"
    
    def backup_database(self, filename=None):
        """Sauvegarde la base de données PostgreSQL"""
        if filename is None:
            filename = self.get_backup_filename('db')
        
        db_settings = settings.DATABASES['default']
        
        # Déterminer la commande selon le type de base
        if db_settings['ENGINE'] == 'django.db.backends.postgresql':
            return self._backup_postgresql(filename, db_settings)
        elif db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            return self._backup_sqlite(filename, db_settings)
        return None
    
    def _backup_postgresql(self, filename, db_settings):
        """Sauvegarde PostgreSQL"""
        import subprocess
        
        host = db_settings.get('HOST', 'localhost')
        port = db_settings.get('PORT', '5432')
        dbname = db_settings['NAME']
        user = db_settings['USER']
        password = db_settings['PASSWORD']
        
        # Créer le fichier SQL
        filepath = os.path.join(self.backup_dir, f"{filename}.sql")
        gz_filepath = f"{filepath}.gz"
        
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        try:
            with open(filepath, 'w') as f:
                subprocess.run(
                    ['pg_dump', '-h', host, '-p', port, '-U', user, '-f', filepath, dbname],
                    env=env,
                    check=True
                )
            
            # Compresser
            with open(filepath, 'rb') as f_in:
                with gzip.open(gz_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(filepath)
            logger.info(f"Backup PostgreSQL créé: {gz_filepath}")
            return gz_filepath
        except Exception as e:
            logger.error(f"Erreur backup PostgreSQL: {e}")
            return None
    
    def _backup_sqlite(self, filename, db_settings):
        """Sauvegarde SQLite"""
        db_path = db_settings['NAME']
        filepath = os.path.join(self.backup_dir, f"{filename}.sqlite")
        gz_filepath = f"{filepath}.gz"
        
        shutil.copy2(db_path, filepath)
        
        with open(filepath, 'rb') as f_in:
            with gzip.open(gz_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(filepath)
        logger.info(f"Backup SQLite créé: {gz_filepath}")
        return gz_filepath
    
    def backup_media(self, filename=None):
        """Sauvegarde les fichiers médias"""
        if filename is None:
            filename = self.get_backup_filename('media')
        
        media_dir = getattr(settings, 'MEDIA_ROOT', None)
        if not media_dir or not os.path.exists(media_dir):
            return None
        
        filepath = os.path.join(self.backup_dir, f"{filename}.tar.gz")
        
        import tarfile
        with tarfile.open(filepath, 'w:gz') as tar:
            tar.add(media_dir, arcname='media')
        
        logger.info(f"Backup media créé: {filepath}")
        return filepath
    
    def backup_static(self, filename=None):
        """Sauvegarde les fichiers statiques"""
        if filename is None:
            filename = self.get_backup_filename('static')
        
        static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None
        if not static_dir or not os.path.exists(static_dir):
            return None
        
        filepath = os.path.join(self.backup_dir, f"{filename}.tar.gz")
        
        import tarfile
        with tarfile.open(filepath, 'w:gz') as tar:
            tar.add(static_dir, arcname='static')
        
        logger.info(f"Backup static créé: {filepath}")
        return filepath
    
    def restore_database(self, backup_file):
        """Restaure la base de données"""
        db_settings = settings.DATABASES['default']
        
        if db_settings['ENGINE'] == 'django.db.backends.postgresql':
            return self._restore_postgresql(backup_file, db_settings)
        elif db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            return self._restore_sqlite(backup_file, db_settings)
        return False
    
    def _restore_postgresql(self, backup_file, db_settings):
        """Restaure PostgreSQL"""
        import subprocess
        
        host = db_settings.get('HOST', 'localhost')
        port = db_settings.get('PORT', '5432')
        dbname = db_settings['NAME']
        user = db_settings['USER']
        password = db_settings['PASSWORD']
        
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Décompresser si nécessaire
        if backup_file.endswith('.gz'):
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as tmp:
                with gzip.open(backup_file, 'rb') as f_in:
                    shutil.copyfileobj(f_in, tmp)
                temp_file = tmp.name
            
            with open(temp_file, 'r') as f:
                subprocess.run(
                    ['psql', '-h', host, '-p', port, '-U', user, '-d', dbname],
                    stdin=f,
                    env=env,
                    check=True
                )
            os.remove(temp_file)
        else:
            with open(backup_file, 'r') as f:
                subprocess.run(
                    ['psql', '-h', host, '-p', port, '-U', user, '-d', dbname],
                    stdin=f,
                    env=env,
                    check=True
                )
        
        logger.info(f"Base restaurée depuis: {backup_file}")
        return True
    
    def _restore_sqlite(self, backup_file, db_settings):
        """Restaure SQLite"""
        db_path = db_settings['NAME']
        
        if backup_file.endswith('.gz'):
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp:
                with gzip.open(backup_file, 'rb') as f_in:
                    shutil.copyfileobj(f_in, tmp)
                temp_file = tmp.name
            
            shutil.copy2(temp_file, db_path)
            os.remove(temp_file)
        else:
            shutil.copy2(backup_file, db_path)
        
        logger.info(f"Base restaurée depuis: {backup_file}")
        return True
    
    def list_backups(self):
        """Liste les sauvegardes disponibles"""
        backups = []
        for f in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, f)
            stat = os.stat(filepath)
            backups.append({
                'name': f,
                'size': stat.st_size,
                'date': datetime.fromtimestamp(stat.st_mtime)
            })
        return sorted(backups, key=lambda x: x['date'], reverse=True)
    
    def clean_old_backups(self, days=30):
        """Supprime les sauvegardes plus anciennes que days"""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = []
        
        for f in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, f)
            if os.path.isfile(filepath):
                if datetime.fromtimestamp(os.stat(filepath).st_mtime) < cutoff:
                    os.remove(filepath)
                    deleted.append(f)
        
        logger.info(f"Supprimé {len(deleted)} anciennes sauvegardes")
        return deleted


class Command(BaseCommand):
    help = 'Sauvegarde automatique de la base de données'

    def add_arguments(self, parser):
        parser.add_argument('--media', action='store_true', help='Sauvegarder aussi les médias')
        parser.add_argument('--static', action='store_true', help='Sauvegarder aussi les fichiers statiques')
        parser.add_argument('--clean', type=int, default=0, help='Supprimer les sauvegardes plus anciennes que N jours')

    def handle(self, *args, **options):
        manager = BackupManager()
        
        # Sauvegarde database
        db_file = manager.backup_database()
        if db_file:
            self.stdout.write(self.style.SUCCESS(f"✓ Base de données sauvegardée: {db_file}"))
        
        # Sauvegarde media
        if options.get('media'):
            media_file = manager.backup_media()
            if media_file:
                self.stdout.write(self.style.SUCCESS(f"✓ Médias sauvegardés: {media_file}"))
        
        # Sauvegarde static
        if options.get('static'):
            static_file = manager.backup_static()
            if static_file:
                self.stdout.write(self.style.SUCCESS(f"✓ Fichiers statiques sauvegardés: {static_file}"))
        
        # Nettoyage
        if options.get('clean', 0) > 0:
            deleted = manager.clean_old_backups(days=options['clean'])
            self.stdout.write(self.style.WARNING(f"✓ {len(deleted)} anciennes sauvegardes supprimées"))
        
        backups = manager.list_backups()
        self.stdout.write(f"\nSauvegardes disponibles: {len(backups)}")
        for b in backups[:5]:
            self.stdout.write(f"  - {b['name']} ({b['size']/1024/1024:.1f} MB)")