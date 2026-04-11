# Guide d'Installation - Système de Gestion Scolaire SyGeS-AM (V2)

## Guide Complet pour Déploiement avec PostgreSQL

---

## Table des Matières

1. [Prérequis Système](#1-prérequis-système)
2. [Phase 1 : Installation des Logiciels](#2-phase-1--installation-des-logiciels)
3. [Phase 2 : Configuration de PostgreSQL](#3-phase-2--configuration-de-postgresql)
4. [Phase 3 : Installation du Projet Django](#4-phase-3--installation-du-projet-django)
5. [Phase 4 : Configuration du Projet](#5-phase-4--configuration-du-projet)
6. [Phase 5 : Initialisation de la Base de Données](#6-phase-5--initialisation-de-la-base-de-données)
7. [Phase 6 : Configuration Réseau et Pare-feu](#7-phase-6--configuration-réseau-et-pare-feu)

---

## 1. Prérequis Système

### 1.1 Spécifications Serveur Recommandées
- **OS** : Windows 10/11 Pro ou Windows Server 2019/2022
- **RAM** : 8 Go minimum (16 Go recommandé)
- **Stockage** : SSD 256 Go minimum
- **Python** : 3.11 ou 3.12

---

## 2. Phase 1 : Installation des Logiciels

### 2.1 Installation de Python
1. Télécharger Python depuis [python.org](https://www.python.org/).
2. **Important** : Cocher "Add Python to PATH" lors de l'installation.

### 2.2 Installation de PostgreSQL
1. Télécharger l'installateur Windows depuis [postgresql.org](https://www.postgresql.org/download/windows/).
2. Suivre l'installation par défaut.
3. Noter le mot de passe du super-utilisateur `postgres` (ex: `AMP50100` utilisé dans la config actuelle).
4. Installer également **pgAdmin 4** (inclus dans l'installateur) pour la gestion graphique.

---

## 3. Phase 2 : Configuration de PostgreSQL

### 3.1 Création de la base de données
1. Ouvrir **pgAdmin 4** ou utiliser la ligne de commande `psql`.
2. Créer une base de données nommée `gestion_scolaire`.
```sql
CREATE DATABASE gestion_scolaire;
```
3. S'assurer que l'utilisateur `postgres` a les droits d'accès.

---

## 4. Phase 3 : Installation du Projet Django

### 4.1 Récupération du code
Extraire les fichiers du projet dans un dossier (ex: `C:\Projets\gestion_ecole`).

### 4.2 Création de l'environnement virtuel
```bash
cd C:\Projets\gestion_ecole
python -m venv venv
.\venv\Scripts\activate
```

### 4.3 Installation des dépendances
```bash
pip install -r requirements.txt
# Assurez-vous d'avoir psycopg2 pour PostgreSQL
pip install psycopg2
```

---

## 5. Phase 4 : Configuration du Projet

### 5.1 Vérification du fichier settings.py
Vérifier la section `DATABASES` dans `core/settings.py` :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gestion_scolaire',
        'USER': 'postgres',
        'PASSWORD': 'VotreMotDePasse',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 6. Phase 5 : Initialisation de la Base de Données

### 6.1 Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6.2 Initialisation des modules
```bash
python manage.py init_modules
```

### 6.3 Création du Super-Utilisateur
```bash
python manage.py createsuperuser
```

---

## 7. Phase 6 : Configuration Réseau et Pare-feu

### 7.1 Ouverture des ports
Si vous souhaitez accéder au serveur depuis d'autres postes du réseau local :
1. Ouvrir le port **8000** (Web) dans le Pare-feu Windows.
2. Ouvrir le port **5432** (PostgreSQL) si la base est sur un autre serveur.

### 7.2 Lancement du serveur
```bash
python manage.py runserver 0.0.0.0:8000
```
L'application sera accessible via `http://[IP_DU_SERVEUR]:8000`.

---

*Dernière mise à jour : 11 Avril 2026*
*Architecture V2 - PostgreSQL*
