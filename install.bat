@echo off
chcp 65001 >nul
echo ========================================
echo   SYSTEME DE GESTION SCOLAIRE
echo   Installation Automatique
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Creation de l'environnement virtuel...
python -m venv venv
if errorlevel 1 (
    echo ERREUR: Impossible de creer l'environnement virtuel
    pause
    exit /b 1
)

echo [2/6] Activation de l'environnement...
call venv\Scripts\activate.bat

echo [3/6] Installation des dependances...
pip install --upgrade pip
pip install Django>=5.0 djangorestframework>=3.14 django-filter>=25.0 python-dotenv>=1.0 Pillow>=10.0 reportlab>=4.0 openpyxl>=3.1
if errorlevel 1 (
    echo ERREUR: Impossible d'installer les dependances
    pause
    exit /b 1
)

echo [4/6] Creation des migrations...
python manage.py makemigrations accounts eleves academics presences finances rapports
if errorlevel 1 (
    echo ERREUR: Impossible de creer les migrations
    pause
    exit /b 1
)

echo [5/6] Application des migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERREUR: Impossible d'appliquer les migrations
    pause
    exit /b 1
)

echo [6/6] Creation du super utilisateur...
echo Le super utilisateur sera cree avec:
echo   Username: admin
echo   Password: admin123
echo.
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123', first_name='Admin', last_name='System', role='direction')
    print('Super utilisateur cree avec succes!')
else:
    print('Le super utilisateur existe deja.')
"

echo.
echo ========================================
echo   INSTALLATION TERMINEE AVEC SUCCES!
echo ========================================
echo.
echo Pour demarrer le serveur:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Acces:
echo   Site: http://localhost:8000
echo   Admin: http://localhost:8000/admin/
echo.
echo Identifiants:
echo   Username: admin
echo   Password: admin123
echo.
pause
