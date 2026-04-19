# Guide d'Installation - Système de Gestion Scolaire SyGeS-AM (V2)

## Guide Complet pour Déploiement avec PostgreSQL

> **📚 Documentation associée** :
> - **[Guide de Test par Rôles](GUIDE_TEST_PAR_ROLES.md)** : Pour tester le système avec chaque rôle utilisateur
> - **[Manuel d'Utilisation](MANUEL_UTILISATION.md)** : Guide d'utilisation quotidienne
> - **[Guide de Test Complet](GUIDE_TEST_COMPLET.md)** : Tests fonctionnels complets

---

## Table des Matières

1. [Prérequis Système](#1-prérequis-système)
2. [Phase 1 : Installation des Logiciels](#2-phase-1--installation-des-logiciels)
3. [Phase 2 : Configuration de PostgreSQL](#3-phase-2--configuration-de-postgresql)
4. [Phase 3 : Installation du Projet Django](#4-phase-3--installation-du-projet-django)
5. [Phase 4 : Configuration du Projet](#5-phase-4--configuration-du-projet)
6. [Phase 5 : Initialisation de la Base de Données](#6-phase-5--initialisation-de-la-base-de-données)
7. [Phase 6 : Création des Utilisateurs et Rôles](#7-phase-6--création-des-utilisateurs-et-rôles)
8. [Phase 7 : Configuration Réseau et Pare-feu](#8-phase-7--configuration-réseau-et-pare-feu)

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

### 5.1 Créer le fichier de configuration `.env`
Le fichier `.env` stocke les informations sensibles (mots de passe, clés secrètes) hors du code source.

1. Copier le fichier exemple :
```bash
copy .env.example .env
```

2. **Éditer le fichier `.env`** avec vos valeurs réelles :

```bash
# === Configuration critique ===
SECRET_KEY= votre-cle-secrete-generee-avec-python
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,votre-ecole.com

# === Base de données ===
DB_NAME=gestion_scolaire
DB_USER=postgres
DB_PASSWORD= votre-mot-de-passe-postgres-fort
DB_HOST=localhost
DB_PORT=5432

# === Sécurité CSRF/CORS ===
CSRF_ALLOW_ALL_ORIGINS=False
CSRF_TRUSTED_ORIGINS=https://votre-ecole.com,https://www.votre-ecole.com
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://votre-ecole.com

# === Email (optionnel) ===
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password-gmail

# === Protection brute-force ===
AXES_ENABLED=True
AXES_FAILURE_LIMIT=5
```

**⚠️ IMPORTANT** : Le fichier `.env` est ignoré par Git (ne sera jamais commité).

3. **Générer une SECRET_KEY sécurisée** :
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
Copier la valeur générée dans `SECRET_KEY` du fichier `.env`

### 5.2 Vérification automatique
Lancer la vérification que tout est correctement configuré :
```bash
python -c "from core.settings import *; print('✓ Configuration OK')"
```

Si vous voyez une erreur, c'est que certaines variables obligatoires sont manquantes.

---

## 6. Phase 5 : Initialisation de la Base de Données

### 6.1 Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6.2 Création du Super-Utilisateur
```bash
python manage.py createsuperuser
```
**Recommandations** :
- Nom d'utilisateur : `admin`
- Mot de passe robuste : minimum 8 caractères avec majuscules, minuscules et chiffres
- Email : votre email administrateur

### 6.3 Initialisation des Modules et Permissions
Cette commande crée tous les services, modules et les permissions par défaut pour chaque rôle :

```bash
python manage.py init_modules
```

**Ce qui est créé automatiquement** :
- 10 services (Scolarité, Enseignement, Finances, etc.)
- Les modules pour chaque service
- Les permissions par défaut pour les rôles : direction, secretaire, comptable, professeur, surveillance

**Important** : Cette commande doit être exécutée après chaque modification des permissions dans `init_modules.py`.

---

## 7. Phase 6 : Création des Utilisateurs et Rôles

> Cette phase est essentielle pour mettre en place les comptes utilisateurs opérationnels. Le Super Admin ne doit être utilisé que pour la configuration technique.

### 7.1 Se connecter en tant que Super Admin
1. Lancer le serveur : `python manage.py runserver`
2. Ouvrir : http://127.0.0.1:8000/
3. Se connecter avec le super-utilisateur créé à l'étape 6.2

### 7.2 Créer les Utilisateurs par Rôle

**Chemin** : **Administration** → **Utilisateurs** → **[Ajouter]**

Créer les comptes suivants pour les tests et l'utilisation quotidienne :

#### Compte Direction
| Champ | Valeur |
|-------|--------|
| Nom d'utilisateur | `direction1` |
| Email | `direction@ecole.fr` |
| Mot de passe | `Direction2026!` |
| Rôle | `direction` |
| Est approuvé | ☑ Cocher |

#### Compte Secrétariat
| Champ | Valeur |
|-------|--------|
| Nom d'utilisateur | `secretaire1` |
| Email | `secretaire@ecole.fr` |
| Mot de passe | `Secretaire2026!` |
| Rôle | `secretaire` |
| Est approuvé | ☑ Cocher |

#### Compte Comptable
| Champ | Valeur |
|-------|--------|
| Nom d'utilisateur | `comptable1` |
| Email | `comptable@ecole.fr` |
| Mot de passe | `Comptable2026!` |
| Rôle | `comptable` |
| Est approuvé | ☑ Cocher |

#### Compte Professeur
| Champ | Valeur |
|-------|--------|
| Nom d'utilisateur | `professeur1` |
| Email | `prof@ecole.fr` |
| Mot de passe | `Professeur2026!` |
| Rôle | `professeur` |
| Est approuvé | ☑ Cocher |

#### Compte Surveillance
| Champ | Valeur |
|-------|--------|
| Nom d'utilisateur | `surveillant1` |
| Email | `surveille@ecole.fr` |
| Mot de passe | `Surveille2026!` |
| Rôle | `surveillance` |
| Est approuvé | ☑ Cocher |

### 7.3 Vérifier les Accès par Rôle

Se déconnecter et tester chaque compte pour vérifier que les permissions sont correctement appliquées :

| Rôle | Modules attendus |
|------|------------------|
| Direction | Tous les modules |
| Secrétaire | Scolarité (CRUD), Enseignement (Lecture) |
| Comptable | Finances (CRUD), Scolarité (Lecture) |
| Professeur | Espace Enseignant, Présences, Notes |
| Surveillance | Présences (CRUD), Discipline (CRUD) |

> **Problème de permission ?** Si un utilisateur voit "Vous n'avez pas l'autorisation", exécuter :
> ```bash
> python manage.py init_modules
> ```

---

## 8. Phase 7 : Configuration Réseau et Pare-feu

### 8.1 Ouverture des ports
Si vous souhaitez accéder au serveur depuis d'autres postes du réseau local :
1. Ouvrir le port **8000** (Web) dans le Pare-feu Windows.
2. Ouvrir le port **5432** (PostgreSQL) si la base est sur un autre serveur.

### 8.2 Lancement du serveur
```bash
python manage.py runserver 0.0.0.0:8000
```
L'application sera accessible via `http://[IP_DU_SERVEUR]:8000`.

---

## 9. Prochaines Étapes après l'Installation

### 9.1 Configuration Initiale de l'Établissement
Utiliser le compte **Direction** pour :
1. Créer l'année scolaire en cours
2. Créer les niveaux scolaires et classes
3. Créer les matières
4. Créer les profils professeurs et attributions

**Guide détaillé** : Voir le **[Guide de Test par Rôles](GUIDE_TEST_PAR_ROLES.md)** - Phase 1

### 9.2 Formation des Utilisateurs
Fournir à chaque utilisateur :
- Ses identifiants de connexion
- Le **[Manuel d'Utilisation](MANUEL_UTILISATION.md)** adapté à son rôle
- Une session de formation sur ses modules spécifiques

### 9.3 Tests de Validation
Avant la mise en production, suivre le **[Guide de Test par Rôles](GUIDE_TEST_PAR_ROLES.md)** pour tester :
- La création de la structure scolaire (Direction)
- L'enregistrement des élèves (Secrétariat)
- La gestion financière (Comptable)
- Les saisies de notes (Professeur)
- Le contrôle des présences (Surveillance)

---

## Dépannage Post-Installation

### Problème : "La variable d'environnement SECRET_KEY doit être définie"
**Cause** : Le fichier `.env` n'existe pas ou ne contient pas SECRET_KEY  
**Solution** :
```bash
# 1. Vérifier que .env existe
dir .env

# 2. Sinon, le créer depuis le modèle
copy .env.example .env

# 3. Générer et ajouter la SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))" >> .env
```

### Problème : "La variable DB_PASSWORD doit être définie en production"
**Cause** : En mode production (DEBUG=False), le mot de passe DB est obligatoire  
**Solution** : Ajouter dans `.env` :
```bash
DB_PASSWORD=votre-mot-de-passe-postgres
```

### Problème : "Votre rôle n'est pas configuré"
**Cause** : L'utilisateur n'a pas de rôle assigné  
**Solution** : Se connecter en Super Admin et vérifier que le rôle est défini (Administration → Utilisateurs)

### Problème : Menu vide ou modules manquants
**Cause** : Les modules ne sont pas initialisés  
**Solution** : Réinitialiser les modules et permissions :
```bash
python manage.py init_modules
```

### Problème : Accès refusé à un module ("Vous n'avez pas l'autorisation")
**Cause** : Mauvais code de module ou permissions non initialisées  
**Solution** :
1. Vérifier que le rôle de l'utilisateur est correct
2. Vérifier que le module est actif (Administration → Gestion des permissions)
3. Réinitialiser les permissions : `python manage.py init_modules`
4. Se déconnecter et se reconnecter

### Problème : CSRF verification failed
**Cause** : Configuration CSRF incorrecte ou domaine non autorisé  
**Solution** : Vérifier dans `.env` que le domaine est dans CSRF_TRUSTED_ORIGINS :
```bash
CSRF_TRUSTED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
```

### Problème : Connexion impossible après 5 tentatives
**Cause** : Protection brute-force (AXES) a bloqué l'IP  
**Solution** : Attendre 30 minutes ou désactiver temporairement :
```bash
# Désactiver AXES (développement uniquement)
set AXES_ENABLED=False
python manage.py runserver
```

---

*Dernière mise à jour : 19 Avril 2026*
*Version : 2.1 - SyGeS-AM*
*Architecture V2 - PostgreSQL*

## Références

- **[Guide de Test par Rôles](GUIDE_TEST_PAR_ROLES.md)** : Guide de test chronologique par rôles utilisateurs
- **[Manuel d'Utilisation](MANUEL_UTILISATION.md)** : Guide d'utilisation quotidienne par rôle
- **[Guide de Test Complet](GUIDE_TEST_COMPLET.md)** : Tests fonctionnels complets (vue Super Admin)
