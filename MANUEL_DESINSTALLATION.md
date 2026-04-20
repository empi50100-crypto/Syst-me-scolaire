# Manuel de Désinstallation et Réinitialisation - SyGeS-AM

**Système de Gestion Scolaire Avancé pour l'Administration Moderne**

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#1-vue-densemble)
2. [Prérequis et Avertissements](#2-prérequis-et-avertissements)
3. [Méthode 1: Réinitialisation Complète (Nuclear Reset)](#3-méthode-1-réinitialisation-complète-nuclear-reset)
4. [Méthode 2: Réinitialisation Sélective par Module](#4-méthode-2-réinitialisation-sélective-par-module)
5. [Méthode 3: Désinstallation Propre](#5-méthode-3-désinstallation-propre)
6. [Vérification Post-Réinitialisation](#6-vérification-post-réinitialisation)
7. [Réinstallation Rapide](#7-réinstallation-rapide)
8. [Dépannage](#8-dépannage)

---

## 1. Vue d'Ensemble

Ce manuel guide le Super Admin dans la désinstallation et réinitialisation complète du système SyGeS-AM. **Ces opérations sont irréversibles** et supprimeront toutes les données.

### ⚠️ Avertissements Critiques

- **Sauvegarde obligatoire** avant toute réinitialisation
- **Tous les utilisateurs** seront déconnectés
- **Toutes les données** (élèves, notes, paiements) seront supprimées
- **Le Super Admin** devra être recréé

### 🎯 Quand Utiliser Ce Manuel

- **Réinitialisation annuelle** (nouvelle année scolaire)
- **Corruption de données** irrécupérable
- **Déménagement serveur** (migration complète)
- **Tests de déploiement** (environnement propre)
- **Fin de contrat** (suppression complète)

---

## 2. Prérequis et Avertissements

### 2.1 Avant de Commencer

#### ✅ Checklist Pré-Réinitialisation

```markdown
□ Sauvegarde complète effectuée (voir MANUEL_UTILISATION.md Section 11)
□ Notification envoyée à tous les utilisateurs (48h avant)
□ Accès Super Admin confirmé (login réussi)
□ Identifiants PostgreSQL disponibles (DB_USER, DB_PASSWORD)
□ Fichier .env accessible et lisible
□ Droits administrateur sur le serveur
□ Heure de maintenance planifiée (hors heures de cours)
```

#### 📦 Matériel Requis

- Accès SSH/RDP au serveur
- Identifiants PostgreSQL (postgres)
- Droits administrateur Windows/Linux
- Environ 30 minutes de disponibilité

### 2.2 Impact sur les Données

| Type de Donnée | Impact Réinitialisation | Sauvegarde Possible? |
|----------------|-------------------------|---------------------|
| **Utilisateurs** | ❌ Tous supprimés | Oui |
| **Élèves** | ❌ Tous supprimés | Oui |
| **Notes** | ❌ Toutes supprimées | Oui |
| **Paiements** | ❌ Tous supprimés | Oui |
| **Documents** | ❌ Tous supprimés | Oui (media/) |
| **Configuration** | ⚠️ Réinitialisée | Oui (.env conservé) |
| **Modules/Permissions** | ✅ Conservés | N/A (réinitialisables) |

---

## 3. Méthode 1: Réinitialisation Complète (Nuclear Reset)

### 🔴 Utilisation

Cette méthode **supprime tout** et remet le système à zéro. Utiliser pour :
- Nouvelle année scolaire (reset complet)
- Corruption majeure de la base
- Démonstration/revente (nettoyage)

### 📋 Étapes

#### Étape 1: Arrêter le Serveur

**Windows (CMD Admin)** :
```cmd
:: Arrêter le serveur Django
Ctrl+C dans la fenêtre de commande

:: Vérifier qu'aucun processus ne tourne
tasklist | findstr python
tasklist | findstr postgres
```

**Linux/macOS** :
```bash
# Arrêter le serveur
pkill -f "python manage.py runserver"
pkill -f gunicorn

# Vérifier les processus
ps aux | grep python
ps aux | grep postgres
```

#### Étape 2: Sauvegarde Finale (Obligatoire)

```bash
:: Windows
python scripts\backup.py

:: Linux/macOS
python scripts/backup.py
```

**Vérifier la sauvegarde** :
```bash
dir backups\daily\  # Windows
ls -lh backups/daily/  # Linux/macOS
```

#### Étape 3: Réinitialisation de la Base PostgreSQL

**Option A: Utiliser le Script Automatique (Recommandé)**

```bash
:: Créer un fichier reset_database.py
@echo off
:: Script de réinitialisation PostgreSQL
python -c "
import os
import subprocess
from dotenv import load_dotenv
load_dotenv('.env')

db_name = os.getenv('DB_NAME', 'gestion_scolaire')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')

if not db_password:
    print('ERREUR: DB_PASSWORD non défini dans .env')
    exit(1)

print(f'Réinitialisation de la base: {db_name}')
env = os.environ.copy()
env['PGPASSWORD'] = db_password

# 1. Supprimer les connexions actives
subprocess.run(['psql', '-h', db_host, '-U', db_user, '-c', 
    f'SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \"{db_name}\" AND pid <> pg_backend_pid();'], env=env)

# 2. Supprimer et recréer la base
subprocess.run(['dropdb', '-h', db_host, '-U', db_user, '--if-exists', db_name], env=env)
result = subprocess.run(['createdb', '-h', db_host, '-U', db_user, db_name], env=env)

if result.returncode == 0:
    print(f'[OK] Base {db_name} recréée avec succès')
else:
    print(f'[ERREUR] Échec création base')
"
```

**Option B: Commandes Manuelles (Windows CMD)** :

```cmd
:: 1. Se connecter à PostgreSQL
psql -U postgres -h localhost

:: 2. Dans l'invite PostgreSQL (\i pour exécuter):
\i -- Terminer les connexions
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'gestion_scolaire' AND pid <> pg_backend_pid();

-- Supprimer la base
DROP DATABASE IF EXISTS gestion_scolaire;

-- Recréer la base vide
CREATE DATABASE gestion_scolaire OWNER postgres ENCODING 'UTF8';

-- Quitter
\q
```

#### Étape 4: Suppression des Migrations

```bash
:: Windows PowerShell
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "migrations" | Where-Object { $_.FullName -notmatch "__pycache__" } | Get-ChildItem -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force

:: Ou manuellement supprimer:
:: - authentification\migrations\0*.py (sauf __init__.py)
:: - core\migrations\0*.py (sauf __init__.py)
:: - enseignement\migrations\0*.py (sauf __init__.py)
:: - finances\migrations\0*.py (sauf __init__.py)
:: - presences\migrations\0*.py (sauf __init__.py)
:: - rapports\migrations\0*.py (sauf __init__.py)
:: - ressources_humaines\migrations\0*.py (sauf __init__.py)
:: - scolarite\migrations\0*.py (sauf __init__.py)
```

**Linux/macOS** :
```bash
# Supprimer les caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Supprimer les migrations (sauf __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
```

#### Étape 5: Suppression des Fichiers Médias (Optionnel)

```bash
:: Conserver la structure, supprimer le contenu
:: Windows
rmdir /s /q media\uploads 2>nul
rmdir /s /q media\documents 2>nul
rmdir /s /q media\photos 2>nul
mkdir media\uploads media\documents media\photos

:: Linux/macOS
rm -rf media/uploads/* media/documents/* media/photos/*
```

#### Étape 6: Recréation Propre

```bash
:: 1. Nouvelles migrations
python manage.py makemigrations authentification core enseignement finances presences rapports ressources_humaines scolarite

:: 2. Application migrations
python manage.py migrate

:: 3. Créer le Super Admin
python manage.py createsuperuser
:: Répondre aux questions:
:: - Nom d'utilisateur: superadmin
:: - Email: admin@ecole.fr
:: - Mot de passe: [fort et sécurisé]

:: 4. Initialiser les modules
python manage.py init_modules

:: 5. Vérification
python manage.py check
python manage.py runserver
```

---

## 4. Méthode 2: Réinitialisation Sélective par Module

### 🟡 Utilisation

Conserver la structure mais vider certaines données uniquement.

### 📊 Modules Réinitialisables

```bash
:: Réinitialiser uniquement les notes (scolarite)
python -c "
from scolarite.models import Note, PeriodeSaisieNotes
Note.objects.all().delete()
PeriodeSaisieNotes.objects.all().delete()
print('[OK] Toutes les notes supprimées')
"

:: Réinitialiser uniquement les paiements (finances)
python -c "
from finances.models import Paiement, Facture
Paiement.objects.all().delete()
Facture.objects.all().delete()
print('[OK] Tous les paiements supprimés')
"

:: Réinitialiser uniquement les élèves (scolarite)
python -c "
from scolarite.models import Eleve, Inscription
Eleve.objects.all().delete()
Inscription.objects.all().delete()
print('[OK] Tous les élèves supprimés')
"

:: Réinitialiser uniquement les utilisateurs (sauf Super Admin)
python -c "
from authentification.models import Utilisateur
Utilisateur.objects.exclude(is_superuser=True).delete()
print('[OK] Tous les utilisateurs (sauf Super Admin) supprimés')
"

:: Réinitialiser les conversations (messages)
python -c "
from authentification.models import Message, Conversation
Message.objects.all().delete()
Conversation.objects.all().delete()
print('[OK] Toutes les conversations supprimées')
"
```

### 📋 Réinitialisation Année Scolaire (Conservant la structure)

```bash
:: Script: reset_annee_scolaire.py
python -c "
from scolarite.models import AnneeScolaire, Eleve, Inscription, Note
from finances.models import Paiement, Facture

print('Réinitialisation pour nouvelle année scolaire...')

# 1. Archiver l'année précédente (optionnel)
# ancienne = AnneeScolaire.objects.filter(actuel=True).first()
# if ancienne:
#     ancienne.actuel = False
#     ancienne.save()

# 2. Supprimer les données de l'année
Note.objects.all().delete()
print('- Notes supprimées')

Paiement.objects.all().delete()
print('- Paiements supprimés')

Facture.objects.all().delete()
print('- Factures supprimées')

Inscription.objects.all().delete()
print('- Inscriptions supprimées')

Eleve.objects.all().delete()
print('- Élèves supprimés')

# 3. Créer nouvelle année (à faire manuellement ou via script)
print('[OK] Prêt pour nouvelle année scolaire')
print('Prochaine étape: Créer la nouvelle année scolaire dans l\'interface')
"
```

---

## 5. Méthode 3: Désinstallation Propre

### 🔵 Utilisation

Suppression complète du projet du serveur (fin de contrat, migration).

### 📋 Étapes de Désinstallation

#### Étape 1: Sauvegarde Complète Finale

```bash
:: Sauvegarde de tout
python scripts\backup.py

:: Copier ailleurs (clé USB, cloud, etc.)
xcopy /e /i /h /k backups\ Z:\Archives\SyGeS-AM_Backup_Final\
```

#### Étape 2: Export des Données Critiques (Optionnel)

```bash
:: Exporter les données en CSV/JSON
python -c "
import csv
import json
from django.core.serializers import serialize

# Élèves
from scolarite.models import Eleve
with open('eleves_export.json', 'w') as f:
    f.write(serialize('json', Eleve.objects.all()))

# Utilisateurs (sans mots de passe)
from authentification.models import Utilisateur
users = Utilisateur.objects.values('username', 'email', 'role', 'first_name', 'last_name')
with open('utilisateurs_export.json', 'w') as f:
    json.dump(list(users), f, indent=2)

print('[OK] Données exportées')
"
```

#### Étape 3: Suppression PostgreSQL

```bash
:: Se connecter en postgres
psql -U postgres -h localhost

:: Commandes SQL:
DROP DATABASE IF EXISTS gestion_scolaire;
DROP USER IF EXISTS syges_user;  -- si utilisateur dédié existait
\q

:: Supprimer le service PostgreSQL (optionnel - Windows)
:: Ne faites PAS ça si d'autres bases sont utilisées!
:: sc delete postgresql-x64-15
```

#### Étape 4: Suppression des Fichiers

```bash
:: Windows
:: 1. Arrêter tous les processus
taskkill /f /im python.exe 2>nul
taskkill /f /im postgres.exe 2>nul

:: 2. Supprimer le répertoire projet
cd C:\
rmdir /s /q "C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole"

:: 3. Supprimer l'environnement virtuel (s'il était dédié)
rmdir /s /q "C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\venv"
```

**Linux/macOS** :
```bash
# Arrêter les processus
pkill -f python
pkill -f postgres

# Supprimer le projet
rm -rf /var/www/syges-am/

# Supprimer l'environnement virtuel
rm -rf /var/www/syges-venv/
```

#### Étape 5: Nettoyage du Système

```bash
:: Windows - Nettoyer les variables d'environnement
setx DB_PASSWORD ""  :: Ne fonctionne pas directement, utiliser l'interface

:: Supprimer les tâches planifiées
schtasks /delete /tn "SyGeS-Backup" /f

:: Supprimer les logs Windows
wevtutil cl Application 2>nul

:: Linux - Nettoyer
unset DB_PASSWORD
unset SECRET_KEY
rm -f ~/.bash_history  :: si mots de passe dedans
```

---

## 6. Vérification Post-Réinitialisation

### ✅ Checklist de Vérification

```markdown
□ Le serveur démarre sans erreur: python manage.py runserver
□ La page de login s'affiche correctement
□ Le Super Admin peut se connecter
□ La base est vide: pas d'élèves, pas de notes
□ Les modules sont initialisés: init_modules exécuté
□ Les migrations sont à jour: python manage.py showmigrations
□ Les médias sont vides (si suppression choisie)
□ Le fichier .env est intact (ne pas l'effacer!)
□ Les logs ne montrent pas d'erreurs critiques
```

### 🔍 Commandes de Vérification

```bash
:: Vérifier la connexion base
cd "C:\Users\AMP\OneDrive\Desktop\Projets\Système scolaire\gestion_ecole"
python -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT current_database(), current_user;')
print('Base:', cursor.fetchone())
"

:: Vérifier les tables (doivent être vides)
python -c "
from scolarite.models import Eleve
from finances.models import Paiement
from authentification.models import Utilisateur
print('Élèves:', Eleve.objects.count())
print('Paiements:', Paiement.objects.count())
print('Utilisateurs (total):', Utilisateur.objects.count())
print('Super Admins:', Utilisateur.objects.filter(is_superuser=True).count())
"
```

**Résultat attendu** :
```
Base: ('gestion_scolaire', 'postgres')
Élèves: 0
Paiements: 0
Utilisateurs (total): 1
Super Admins: 1
```

---

## 7. Réinstallation Rapide

### 🚀 Installation Express (Après Reset)

```bash
:: 1. Cloner depuis GitHub (si suppression complète)
git clone https://github.com/empi50100-crypto/Syst-me-scolaire.git

:: 2. Recréer environnement virtuel
python -m venv venv
venv\Scripts\activate

:: 3. Dépendances
pip install -r requirements.txt

:: 4. Configuration
:: - Le fichier .env doit exister avec SECRET_KEY et DB_PASSWORD
:: - Si supprimé: copy .env.example .env et éditer

:: 5. Base de données (créée si n'existe pas)
python manage.py migrate

:: 6. Super Admin
python manage.py createsuperuser

:: 7. Modules
python manage.py init_modules

:: 8. Lancer
python manage.py runserver
```

---

## 8. Dépannage

### Problème: "La base n'existe pas"

```bash
:: Créer manuellement
psql -U postgres -c "CREATE DATABASE gestion_scolaire OWNER postgres ENCODING 'UTF8';"
```

### Problème: "Permission denied sur PostgreSQL"

```bash
:: Windows - Lancer CMD en Admin
:: Linux/macOS
sudo -u postgres psql

:: Puis dans psql:
ALTER USER postgres WITH PASSWORD 'votre_nouveau_mot_de_passe';
\q

:: Mettre à jour .env avec le nouveau mot de passe
```

### Problème: "Les migrations échouent"

```bash
:: Forcer la réinitialisation
python manage.py migrate --fake-initial

:: Ou supprimer et recréer
python manage.py migrate --run-syncdb
```

### Problème: "Impossible de supprimer la base (connexions actives)"

```bash
:: Forcer la déconnexion
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
import psycopg2

conn = psycopg2.connect(
    dbname='postgres',
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST', 'localhost')
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute(\"\"\"
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE datname = 'gestion_scolaire' 
    AND pid <> pg_backend_pid();
\"\"\")
print('[OK] Connexions terminées')
conn.close()
"
```

### Problème: "Le Super Admin ne peut pas se connecter"

```bash
:: Réinitialiser le mot de passe Super Admin
python manage.py changepassword superadmin

:: Ou recréer complètement
python manage.py shell
>>> from authentification.models import Utilisateur
>>> u = Utilisateur.objects.get(username='superadmin')
>>> u.set_password('NouveauMotDePasse123!')
>>> u.save()
>>> exit()
```

---

## 📞 Support

En cas de problème critique :

1. **Consulter les logs** : `logs/backup.log`, `logs/django.log`
2. **Vérifier la dernière sauvegarde** : `backups/daily/`
3. **Restaurer depuis backup** : `python scripts/backup.py --restore backups/daily/...`
4. **Documentation** : Consulter `GUIDE_INSTALLATION.md`
5. **GitHub** : https://github.com/empi50100-crypto/Syst-me-scolaire

---

*Dernière mise à jour : 20 Avril 2026*
*Version : 1.0 - SyGeS-AM*
*Destiné exclusivement au Super Admin*
