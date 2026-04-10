@echo off
REM ==============================================
REM Script de déploiement sécurisé - Windows
REM Système de Gestion Scolaire
REM ==============================================

echo ==============================================
echo DEPLOIEMENT SECURISE - SYSTEME SCOLAIRE
echo ==============================================

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé
    exit /b 1
)

REM Vérifier .env
if not exist ".env" (
    echo ERREUR: Le fichier .env n'existe pas
    echo Copiez .env.example vers .env et configurez-le
    exit /b 1
)

echo.
echo etape 1: Installation des dépendances...
pip install -r requirements.txt

echo.
echo etape 2: Vérification Django...
python manage.py check

echo.
echo etape 3: Migration de la base de données...
python manage.py migrate

echo.
echo etape 4: Collecte des fichiers statiques...
python manage.py collectstatic --noinput

echo.
echo etape 5: Création du superutilisateur...
python manage.py createsuperuser

echo.
echo ==============================================
echo DEPLOIEMENT TERMINE AVEC SUCCES
echo ==============================================
echo.
echo Prochaines étapes:
echo 1. Configurer Nginx avec SSL (voir DEPLOYMENT_SECURITY_CHECKLIST.md)
echo 2. Planifier les sauvegardes automatiques (schtasks)
echo 3. Tester HTTPS et les headers de sécurité
echo.
pause
