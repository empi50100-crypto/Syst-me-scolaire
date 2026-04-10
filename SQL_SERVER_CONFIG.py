"""
Configuration SQL Server pour Django
Ajoutez ce contenu dans core/settings.py pour utiliser SQL Server
"""

# Assurez-vous d'abord d'installer les dépendances:
# pip install django-pyodbc-azure pyodbc

# Modifier DATABASES dans settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# VERSION SQL SERVER (décommenter et commenter la version SQLite):
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlserver_ado',
        'NAME': 'GestionEcole',
        'SERVER': 'localhost\\SQLEXPRESS',  # ou 'localhost' si instance par défaut
        'USER': 'sa',
        'PASSWORD': 'YourPassword',
        'OPTIONS': {
            'provider': 'SQLOLEDB',
            'MARS_Connection': True,
        },
    }
}
"""

# Alternative avec pyodbc:
"""
import pyodbc

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'GestionEcole',
        'SERVER': 'localhost\\SQLEXPRESS',
        'DRIVER': 'ODBC Driver 17 for SQL Server',
        'Trusted_Connection': 'yes',  # Windows Authentication
        # Ou avec SQL Authentication:
        # 'UID': 'sa',
        # 'PWD': 'YourPassword',
    }
}
"""
