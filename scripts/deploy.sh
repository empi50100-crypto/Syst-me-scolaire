#!/bin/bash
# ==============================================
# Script de déploiement sécurisé - Linux
# Système de Gestion Scolaire
# ==============================================

set -e

echo "=============================================="
echo "DEPLOIEMENT SECURISE - SYSTEME SCOLAIRE"
echo "=============================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python3 n'est pas installé"
    exit 1
fi

# Vérifier .env
if [ ! -f ".env" ]; then
    echo "ERREUR: Le fichier .env n'existe pas"
    echo "Copiez .env.example vers .env et configurez-le"
    exit 1
fi

echo ""
echo "etape 1: Installation des dépendances..."
pip install -r requirements.txt

echo ""
echo "etape 2: Vérification Django..."
python manage.py check

echo ""
echo "etape 3: Migration de la base de données..."
python manage.py migrate

echo ""
echo "etape 4: Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo ""
echo "etape 5: Création du superutilisateur..."
python manage.py createsuperuser

echo ""
echo "=============================================="
echo "DEPLOIEMENT TERMINE AVEC SUCCES"
echo "=============================================="
echo ""
echo "Prochaines étapes:"
echo "1. Configurer Nginx avec SSL (voir DEPLOYMENT_SECURITY_CHECKLIST.md)"
echo "2. Planifier les sauvegardes automatiques (cron)"
echo "3. Tester HTTPS et les headers de sécurité"
