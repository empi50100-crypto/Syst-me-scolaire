#!/bin/bash

echo "========================================"
echo "  SYSTEME DE GESTION SCOLAIRE"
echo "  Installation Automatique (Linux/Mac)"
echo "========================================"
echo ""

# Create virtual environment
echo "[1/6] Creation de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERREUR: Impossible de creer l'environnement virtuel"
    exit 1
fi

# Activate virtual environment
echo "[2/6] Activation de l'environnement..."
source venv/bin/activate

# Install dependencies
echo "[3/6] Installation des dependances..."
pip install --upgrade pip
pip install Django>=5.0 djangorestframework>=3.14 django-filter>=25.0 python-dotenv>=1.0 Pillow>=10.0 reportlab>=4.0 openpyxl>=3.1
if [ $? -ne 0 ]; then
    echo "ERREUR: Impossible d'installer les dependances"
    exit 1
fi

# Create migrations
echo "[4/6] Creation des migrations..."
python manage.py makemigrations accounts eleves academics presences finances rapports
if [ $? -ne 0 ]; then
    echo "ERREUR: Impossible de creer les migrations"
    exit 1
fi

# Apply migrations
echo "[5/6] Application des migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERREUR: Impossible d'appliquer les migrations"
    exit 1
fi

# Create superuser
echo "[6/6] Creation du super utilisateur..."
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

echo ""
echo "========================================"
echo "  INSTALLATION TERMINEE AVEC SUCCES!"
echo "========================================"
echo ""
echo "Pour demarrer le serveur:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Acces:"
echo "  Site: http://localhost:8000"
echo "  Admin: http://localhost:8000/admin/"
echo ""
echo "Identifiants:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
