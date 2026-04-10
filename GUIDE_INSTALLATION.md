# Guide d'Installation - Système de Gestion Scolaire SyGeS-AM

## Guide Complet pour Déploiement en Réseau Local avec SQL Server

---

## Table des Matières

1. [Prérequis Système](#1-prérequis-système)
2. [Phase 1 : Installation des Logiciels sur le Serveur](#2-phase-1--installation-des-logiciels-sur-le-serveur)
3. [Phase 2 : Configuration de SQL Server](#3-phase-2--configuration-de-sql-server)
4. [Phase 3 : Création de la Base de Données](#4-phase-3--création-de-la-base-de-données)
5. [Phase 4 : Installation du Projet Django](#5-phase-4--installation-du-projet-django)
6. [Phase 5 : Configuration du Projet](#6-phase-5--configuration-du-projet)
7. [Phase 6 : Préparation du Serveur Web](#7-phase-6--préparation-du-serveur-web)
8. [Phase 7 : Configuration Réseau](#8-phase-7--configuration-réseau)
9. [Phase 8 : Test et Vérification](#9-phase-8--test-et-vérification)
10. [Annexes](#10-annexes)

---

## 1. Prérequis Système

### 1.1 Spécifications Matérielles Minimales (Serveur)

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| Processeur | Intel Core i5 (4 cœurs) | Intel Core i7/i9 (6+ cœurs) |
| Mémoire RAM | 8 Go | 16 Go |
| Disque Dur | 256 Go SSD | 512 Go SSD |
| Carte Réseau | 1 Gbps | 1 Gbps |
| Système d'exploitation | Windows Server 2019 / Windows 10/11 Pro | Windows Server 2022 |

### 1.2 Spécifications pour les Postes Clients

| Composant | Minimum |
|-----------|---------|
| Processeur | Intel Core i3 / AMD Ryzen 3 |
| Mémoire RAM | 4 Go |
| Navigateur | Chrome, Firefox, Edge (versions récentes) |
| Connexion | 10 Mbps minimum |

### 1.3 Architecture du Réseau

```
┌─────────────────────────────────────────────────────────────────┐
│                        RÉSEAU LOCAL (LAN)                        │
│                                                                  │
│    ┌──────────────────┐                                         │
│    │   SERVEUR        │                                         │
│    │  - Windows OS     │                                         │
│    │  - SQL Server     │◄──── Port 1433 (SQL)                  │
│    │  - Django/Python  │◄──── Port 8000 (Web)                  │
│    │  - Gunicorn/Nginx │                                         │
│    └──────────────────┘                                         │
│            │                                                     │
│            │ IP: 192.168.1.100 (exemple)                        │
│            │                                                     │
├────────────┼─────────────────────────────────────────────────────┤
│            │                                                     │
│   ┌────────▼────────┐   ┌────────┐   ┌────────┐              │
│   │  Poste 1        │   │Poste 2 │   │Poste 3 │              │
│   │  (Direction)    │   │(Sec.)  │   │(Compt.)│              │
│   │  192.168.1.10  │   │.11     │   │.12     │              │
│   └─────────────────┘   └────────┘   └────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase 1 : Installation des Logiciels sur le Serveur

### 2.1 Installation de Windows (si non installé)

1. Installer Windows Server 2019/2022 ou Windows 10/11 Pro
2. Nom d'hôte recommandé : `SERVEUR-ECOLE`
3. Configuration réseau :
   - IP fixe : `192.168.1.100`
   - Masque : `255.255.255.0`
   - Passerelle : `192.168.1.1`
   - DNS : `192.168.1.100` (serveur lui-même)

### 2.2 Installation de Python

**Étape 2.2.1 : Télécharger Python**

1. Aller sur : https://www.python.org/downloads/
2. Télécharger Python 3.11.x ou 3.12.x (version 64-bit)
3. **Important** : Cocher "Add Python to PATH" lors de l'installation
4. Cliquer "Install Now"

**Étape 2.2.2 : Vérifier l'installation**

Ouvrir CMD et exécuter :
```cmd
python --version
pip --version
```

**Résultat attendu :**
```
Python 3.11.8
pip 24.0 from C:\Python311\lib\site-packages\pip (python 3.11)
```

### 2.3 Installation de Visual Studio Build Tools

**Étape 2.3.1 : Télécharger**

1. Télécharger depuis : https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Exécuter `vs_buildtools.exe`

**Étape 2.3.2 : Installer**

1. Cocher "Desktop development with C++"
2. Dans "Summary", vérifier que ces composants sont sélectionnés :
   - MSVC v143 - VS 2022 C++ x64/x86 build tools
   - Windows 11 SDK (ou Windows 10 SDK)
3. Cliquer "Install"
4. Redémarrer si demandé

### 2.4 Installation de SQL Server

**Option A : SQL Server Express (Gratuit, recommandé pour test)**

**Étape 2.4.1 : Télécharger**

1. Aller sur : https://www.microsoft.com/fr-fr/sql-server/sql-server-downloads
2. Télécharger "SQL Server 2022 Express"

**Étape 2.4.2 : Installer**

1. Exécuter le fichier téléchargé
2. Choisir "Basic" ou "Custom"
3. Accepter les termes de licence
4. Choisir l'emplacement d'installation
5. Cliquer "Install"

**Étape 2.4.3 : Configuration Post-Installation**

1. Ouvrir "SQL Server Configuration Manager"
2. Activer TCP/IP :
   - SQL Server Network Configuration → Protocols for SQLEXPRESS
   - Activer "TCP/IP"
   - Propriétés → IP Addresses → TCP Port = 1433
3. Redémarrer le service SQL Server

**Option B : SQL Server Developer (Complet, pour production)**

1. Télécharger depuis le lien ci-dessus
2. Sélectionner "Developer"
3. Suivre les mêmes étapes que Express

### 2.5 Installation de SQL Server Management Studio (SSMS)

1. Télécharger depuis : https://learn.microsoft.com/fr-fr/sql/ssms/download-sql-server-management-studio-ssms
2. Exécuter l'installateur
3. Cliquer "Install"
4. Lancer SSMS

### 2.6 Installation de Git

1. Télécharger depuis : https://git-scm.com/download/win
2. Exécuter l'installateur
3. Cocher "Add Git to PATH"
4. Utiliser les options par défaut

---

## 3. Phase 2 : Configuration de SQL Server

### 3.1 Connexion à SQL Server

1. Lancer SQL Server Management Studio (SSMS)
2. Fenêtre de connexion :
   - Server type : Database Engine
   - Server name : `localhost` ou `.\SQLEXPRESS`
   - Authentication : Windows Authentication (si local) ou SQL Server Authentication

### 3.2 Activation de l'Authentification Mixte

**Via SSMS :**

1. Clic droit sur le serveur → Properties → Security
2. Server authentication → SQL Server and Windows Authentication mode
3. Cliquer OK
4. Redémarrer le service SQL Server

**Via CMD (PowerShell en tant qu'Admin) :**

```powershell
# Redémarrer le service SQL
Restart-Service -Name "MSSQLSERVER" -Force
```

### 3.3 Création de la Base de Données

**Requêtes SQL à exécuter dans SSMS :**

```sql
-- =============================================
-- CRÉATION DE LA BASE DE DONNÉES
-- =============================================

-- Créer la base de données
CREATE DATABASE SyGeSAM_DB;
GO

-- Vérifier la création
SELECT name, state_desc, create_date 
FROM sys.databases 
WHERE name = 'SyGeSAM_DB';
GO

-- =============================================
-- CRÉATION DE LA CONNEXION SQL SERVER
-- =============================================

-- Créer un login pour l'application Django
CREATE LOGIN SyGeSAM_User 
WITH PASSWORD = 'Votr3M0tDeP@ss3!2024';
GO

-- Attribuer les droits sur la base
USE SyGeSAM_DB;
GO

CREATE USER SyGeSAM_User FOR LOGIN SyGeSAM_User;
GO

ALTER ROLE db_owner ADD MEMBER SyGeSAM_User;
GO

-- =============================================
-- CRÉATION DES SCHÉMAS (optionnel)
-- =============================================

CREATE SCHEMA eleves;
GO
CREATE SCHEMA finances;
GO
CREATE SCHEMA academics;
GO
CREATE SCHEMA presences;
GO

-- Attribuer les schémas à l'utilisateur
ALTER USER SyGeSAM_User WITH DEFAULT_SCHEMA = dbo;
GO

-- =============================================
-- VÉRIFICATION FINALE
-- =============================================

-- Lister les bases de données
SELECT 
    name AS DatabaseName,
    state_desc AS Status,
    user_access_desc AS UserAccess,
    create_date AS CreatedDate
FROM sys.databases
ORDER BY name;
GO

-- Vérifier les connexions
SELECT 
    name AS LoginName,
    type_desc AS LoginType,
    is_disabled AS IsDisabled
FROM sys.server_principals
WHERE type IN ('S', 'U')
ORDER BY name;
GO

-- Tester la connexion de l'utilisateur
USE SyGeSAM_DB;
GO

SELECT 
    USER_NAME() AS CurrentUser,
    USER_ID() AS CurrentUserID,
    DB_NAME() AS DatabaseName;
GO
```

### 3.4 Configuration du Pare-feu Windows

**Via PowerShell (Admin) :**

```powershell
# Règle pour SQL Server
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow

# Règle pour le service Django (port 8000)
New-NetFirewallRule -DisplayName "Django App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

**Vérification :**

```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*SQL*" -or $_.DisplayName -like "*Django*"}
```

### 3.5 Configuration SQL Server pour Accès Réseau

**Via SQL Server Configuration Manager :**

1. SQL Server Network Configuration → Protocols for SQLEXPRESS
2. Activer "TCP/IP"
3. Propriétés → IP Addresses :
   - IP1 (127.0.0.1) : Active = Yes, TCP Port = 1433
   - IP ALL : TCP Port = 1433
4. SQL Server Services → Redémarrer SQL Server

---

## 4. Phase 3 : Création de la Base de Données (Suite)

### 4.1 Script SQL Complet de Préparation

```sql
-- =============================================
-- SCRIPT DE PRÉPARATION SYGeS-AM
-- Base de données : SyGeSAM_DB
-- =============================================

USE master;
GO

-- Vérifier si la base existe, la supprimer si oui
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'SyGeSAM_DB')
BEGIN
    ALTER DATABASE SyGeSAM_DB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE SyGeSAM_DB;
END
GO

-- Créer la nouvelle base
CREATE DATABASE SyGeSAM_DB;
GO

USE SyGeSAM_DB;
GO

-- =============================================
-- CRÉATION DES TABLES (Structure minimale)
-- =============================================

-- Table des années scolaires
CREATE TABLE finances_anneescolaire (
    id INT IDENTITY(1,1) PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    est_active BIT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des classes
CREATE TABLE academics_classe (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    niveau VARCHAR(10) NOT NULL,
    filiere VARCHAR(50) NULL,
    capacite INT DEFAULT 40,
    annee_scolaire_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des matières
CREATE TABLE academics_matiere (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    coefficient INT DEFAULT 1,
    classe_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des élèves
CREATE TABLE eleves_eleve (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NULL,
    sexe VARCHAR(10) NULL,
    adresse TEXT NULL,
    telephone_parent VARCHAR(20) NULL,
    matricule VARCHAR(50) NULL,
    statut VARCHAR(20) DEFAULT 'actif',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des inscriptions
CREATE TABLE eleves_inscription (
    id INT IDENTITY(1,1) PRIMARY KEY,
    eleve_id INT NOT NULL,
    classe_id INT NOT NULL,
    annee_scolaire_id INT NOT NULL,
    date_inscription DATE DEFAULT CAST(GETDATE() AS DATE),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des utilisateurs (compte Django)
CREATE TABLE accounts_user (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) NULL,
    first_name VARCHAR(150) NULL,
    last_name VARCHAR(150) NULL,
    role VARCHAR(20) DEFAULT 'direction',
    is_active BIT DEFAULT 1,
    is_staff BIT DEFAULT 0,
    is_superuser BIT DEFAULT 0,
    last_login DATETIME NULL,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des présences
CREATE TABLE presences_presence (
    id INT IDENTITY(1,1) PRIMARY KEY,
    eleve_id INT NOT NULL,
    classe_id INT NOT NULL,
    date DATE NOT NULL,
    statut VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- Table des évaluations/notes
CREATE TABLE academics_evaluation (
    id INT IDENTITY(1,1) PRIMARY KEY,
    eleve_id INT NOT NULL,
    matiere_id INT NOT NULL,
    type_eval VARCHAR(20) NOT NULL,
    titre VARCHAR(100) NULL,
    date_eval DATE NOT NULL,
    note DECIMAL(5,2) NOT NULL,
    coefficient INT DEFAULT 1,
    annee_scolaire_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
GO

-- =============================================
-- CRÉATION DES INDEX
-- =============================================

CREATE NONCLUSTERED INDEX IX_eleve_nom ON eleves_eleve(nom);
CREATE NONCLUSTERED INDEX IX_eleve_matricule ON eleves_eleve(matricule);
CREATE NONCLUSTERED INDEX IX_inscription_eleve ON eleves_inscription(eleve_id);
CREATE NONCLUSTERED INDEX IX_presence_date ON presences_presence(date);
CREATE NONCLUSTERED INDEX IX_evaluation_eleve ON academics_evaluation(eleve_id);
GO

-- =============================================
-- DONNÉES DE TEST (optionnel)
-- =============================================

-- Année scolaire active
INSERT INTO finances_anneescolaire (libelle, date_debut, date_fin, est_active)
VALUES ('2025-2026', '2025-09-01', '2026-07-15', 1);
GO

-- Utilisateur administrateur par défaut (password: admin123 - à changer!)
-- Le hash sera généré par Django lors de la première migration
INSERT INTO accounts_user (username, email, first_name, last_name, role, is_active, is_staff, is_superuser)
VALUES ('admin', 'admin@ecole.com', 'Administrateur', 'Système', 'superadmin', 1, 1, 1);
GO

-- =============================================
-- VÉRIFICATION
-- =============================================

SELECT 'Base de données créée avec succès!' AS Statut, SYSDATETIME() AS DateCreation;
GO

-- Lister toutes les tables
SELECT 
    TABLE_SCHEMA + '.' + TABLE_NAME AS TableName,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = 'SyGeSAM_DB'
ORDER BY TABLE_SCHEMA, TABLE_NAME;
GO
```

### 4.2 Sauvegarde de la Configuration

Créer un fichier `config_serveur.txt` sur le bureau :

```
=============================================
CONFIGURATION SERVEUR - SYGeS-AM
=============================================

Serveur SQL Server
- Nom du serveur : SERVEUR-ECOLE
- Instance : SQLEXPRESS (ou MSSQLSERVER)
- Base de données : SyGeSAM_DB
- Utilisateur : SyGeSAM_User
- Port : 1433
- Chaîne de connexion :
  Server=SERVEUR-ECOLE\SQLEXPRESS;Database=SyGeSAM_DB;User Id=SyGeSAM_User;Password=Votr3M0tDeP@ss3!2024;TrustServerCertificate=yes;

Application Django
- Port : 8000
- URL réseau : http://192.168.1.100:8000

Comptes par défaut
- Admin Django : admin / (à définir lors de la première connexion)

=============================================
```

---

## 5. Phase 4 : Installation du Projet Django

### 5.1 Création du Répertoire du Projet

```cmd
# Ouvrir CMD (PowerShell) en tant qu'administrateur

# Créer le dossier du projet
mkdir C:\SyGeS-AM
cd C:\SyGeS-AM

# Vérifier
dir
```

### 5.2 Installation des Dépendances Python

```cmd
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances principales
pip install django==5.0.4
pip install djangorestframework==3.15.1
pip install django-cors-headers==4.3.1
pip install django-axes==6.0.0
pip install django-simplejwt==5.3.1

# Base de données SQL Server
pip install pyodbc==5.0.1
pip install django-pyodbc-azure==2.1.0.0

# PDF et rapports
pip install reportlab==4.1.0

# Authentification 2FA
pip install pyotp==2.9.0
pip install qrcode==7.4.2
pip install pillow==10.2.0

# Sécurité
pip install cryptography==42.0.5

# Autres dépendances
pip install python-decouple==3.8
pip install whitenoise==5.3.0
pip install gunicorn==21.2.0

# Vérifier les installations
pip list
```

### 5.3 Installation du Projet depuis GitHub (si disponible)

```cmd
cd C:\SyGeS-AM

# Cloner le dépôt (remplacer par l'URL réelle)
git clone https://github.com/votre-username/syges-am.git .

# Ou extraire le fichier ZIP du projet

# Vérifier le contenu
dir
```

### 5.4 Structure Attendue du Projet

```
C:\SyGeS-AM\
├── gestion_ecole\           # Application principale Django
│   ├── accounts\            # Gestion des comptes
│   ├── academics\           # Gestion académique
│   ├── eleves\              # Gestion des élèves
│   ├── finances\            # Finances
│   ├── presences\           # Présences
│   ├── rapports\            # Rapports
│   ├── core\                # Configuration core
│   ├── templates\           # Templates HTML
│   ├── static\             # Fichiers statiques
│   ├── manage.py            # Script Django
│   └── settings.py          # Configuration
├── venv\                    # Environnement virtuel (à créer)
├── requirements.txt         # Liste des dépendances
└── .env                     # Variables d'environnement
```

---

## 6. Phase 5 : Configuration du Projet

### 6.1 Création du Fichier .env

Créer le fichier `C:\SyGeS-AM\.env` :

```env
# =============================================
# CONFIGURATION SYGeS-AM - ENVIRONNEMENT
# =============================================

# Mode DEBUG (False en production)
DEBUG=False

# Clé secrète Django (générer une nouvelle en production!)
SECRET_KEY=VotreClefSecret123!@#$%^&*()+=_

# Domaine autorisé
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1,SERVEUR-ECOLE

# Base de données SQL Server
DB_ENGINE=sql_server.pyodbc
DB_NAME=SyGeSAM_DB
DB_SERVER=SERVEUR-ECOLE\SQLEXPRESS
DB_PORT=1433
DB_USER=SyGeSAM_User
DB_PASSWORD=Votr3M0tDeP@ss3!2024

# Configuration SQL Server
DB_TRUST_SERVER_CERTIFICATE=True

# Authentification
AUTH_USER_MODEL=accounts.User

# Timezone
TIME_ZONE=Africa/Porto-Novo
LANGUAGE_CODE=fr
```

### 6.2 Configuration de settings.py

**Section Base de Données (gestion_ecole\settings.py) :**

```python
# =============================================
# CONFIGURATION BASE DE DONNÉES - SQL SERVER
# =============================================

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': env('DB_NAME', default='SyGeSAM_DB'),
        'USER': env('DB_USER', default='SyGeSAM_User'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_SERVER', default='localhost\\SQLEXPRESS'),
        'PORT': env('DB_PORT', default='1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'TrustServerCertificate': 'Yes',
            'Connection Timeout': 30,
        },
    }
}
```

### 6.3 Installation de ODBC Driver

**Étape 6.3.1 : Télécharger**

1. Aller sur : https://learn.microsoft.com/fr-fr/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Télécharger "ODBC Driver 17 for SQL Server"

**Étape 6.3.2 : Installer**

1. Exécuter le fichier `msodbcsql.msi`
2. Accepter la licence
3. Cliquer "Next" jusqu'à "Finish"

**Vérification :**

```powershell
# Lister les pilotes ODBC installés
Get-OdbcDriver | Select-Object Name, Platform
```

### 6.4 Création du Superutilisateur Django

```cmd
cd C:\SyGeS-AM\gestion_ecole

# Appliquer les migrations
python manage.py migrate

# Créer le superutilisateur
python manage.py createsuperuser

# Suivre les instructions :
# Username: admin
# Email: admin@ecole.com
# Password: ************
# Confirm password: ************
```

### 6.5 Collecte des Fichiers Statiques

```cmd
cd C:\SyGeS-AM\gestion_ecole

# Créer le dossier static s'il n'existe pas
mkdir staticfiles

# Collecter les fichiers statiques
python manage.py collectstatic

# Répondre "yes" pour confirmer
```

---

## 7. Phase 6 : Préparation du Serveur Web

### 7.1 Option A : Exécution Directe (Test)

```cmd
cd C:\SyGeS-AM\gestion_ecole

# Démarrer le serveur
python manage.py runserver 0.0.0.0:8000
```

**Vérification locale :**
- Ouvrir un navigateur sur le serveur
- Aller sur : http://localhost:8000

### 7.2 Option B : Gunicorn (Production)

**Création du fichier `run_gunicorn.bat` :**

```batch
@echo off
cd C:\SyGeS-AM\gestion_ecole
C:\SyGeS-AM\venv\Scripts\activate
gunicorn gestion_ecole.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

**Création du service Windows :**

```powershell
# Créer le service avec NSSM (Non-Sucking Service Manager)

# Télécharger NSSM
Invoke-WebRequest -Uri https://nssm.cc/release/nssm-2.24.zip -OutFile C:\nssm.zip
Expand-Archive -Path C:\nssm.zip -DestinationPath C:\nssm

# Installer en tant que service
C:\nssm\win64\nssm.exe install SyGeS-AM "C:\SyGeS-AM\venv\Scripts\python.exe" "C:\SyGeS-AM\run_gunicorn.bat"

# Configurer le service
C:\nssm\win64\nssm.exe set SyGeS-AM AppDirectory "C:\SyGeS-AM\gestion_ecole"
C:\nsm\win64\nssm.exe set SyGeS-AM AppStdout "C:\SyGeS-AM\logs\gunicorn.log"
C:\nssm\win64\nssm.exe set SyGeS-AM AppStderr "C:\nssm\win64\nssm.exe set SyGeS-AM AppStderr "C:\SyGeS-AM\logs\error.log"

# Démarrer le service
Start-Service SyGeS-AM
```

### 7.3 Option C : IIS (Recommandé pour Windows Server)

**Installation du Module IIS :**

1. Ouvrir "Server Manager"
2. Manage → Add Roles and Features
3. Next → Next → Select server
4. Cocher "Web Server (IIS)"
5. Ajouter les services de rôle nécessaires
6. Installer

**Installation de wfastcgi :**

```cmd
pip install wfastcgi
python -m wfastcgi enable
```

**Configuration dans IIS :**

1. Ouvrir IIS Manager
2. Ajouter un nouveau Site :
   - Nom : SyGeS-AM
   - Physical path : C:\SyGeS-AM\gestion_ecole
   - Binding : Port 8000
3. Configuration de wfastcgi dans web.config

---

## 8. Phase 7 : Configuration Réseau

### 8.1 Configuration IP Fixe sur le Serveur

**Via les paramètres Windows :**

1. Paramètres → Réseau → Ethernet → Modifier les options IP
2. Modifier :
   - Adresse IP : 192.168.1.100
   - Masque de sous-réseau : 255.255.255.0
   - Passerelle par défaut : 192.168.1.1
   - DNS préféré : 192.168.1.100

**Via PowerShell :**

```powershell
# Obtenir le nom de l'adaptateur
Get-NetAdapter

# Configurer l'IP fixe
$interface = "Ethernet"
$ip = "192.168.1.100"
$gateway = "192.168.1.1"
$dns = "192.168.1.100"

# Supprimer la config existante
Remove-NetIPAddress -InterfaceAlias $interface -Confirm:$false
Remove-NetRoute -InterfaceAlias $interface -Confirm:$false

# Ajouter la nouvelle configuration
New-NetIPAddress -InterfaceAlias $interface -IPAddress $ip -PrefixLength 24 -DefaultGateway $gateway
Set-DnsClientServerAddress -InterfaceAlias $interface -ServerAddresses $dns
```

### 8.2 Configuration du Pare-feu pour Accès Réseau

```powershell
# Règle pour SQL Server
New-NetFirewallRule -DisplayName "SQL Server Remote" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow -RemoteAddress 192.168.1.0/24

# Règle pour Django
New-NetFirewallRule -DisplayName "Django App Remote" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -RemoteAddress 192.168.1.0/24

# Vérification
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*SQL*" -or $_.DisplayName -like "*Django*"}
```

### 8.3 Vérification de la Connectivité

**Depuis le serveur :**

```cmd
# Tester SQL Server local
sqlcmd -S localhost\SQLEXPRESS -E

# À l'intérieur de sqlcmd :
SELECT @@VERSION;
GO
EXIT
```

**Depuis un poste client :**

```cmd
# Ping vers le serveur
ping 192.168.1.100

# Test du port SQL Server
tnc 192.168.1.100 -Port 1433

# Test de l'application web
curl http://192.168.1.100:8000

# Ou simplement ouvrir dans le navigateur :
# http://192.168.1.100:8000
```

### 8.4 Configuration des Postes Clients

**Sur chaque poste client :**

1. Ouvrir un navigateur (Chrome recommandé)
2. Aller sur : http://192.168.1.100:8000
3. La page d'accueil doit s'afficher

**Création d'un raccourci :**

1. Clic droit sur le bureau → Nouveau → Raccourci
2. URL : `http://192.168.1.100:8000`
3. Nom : "SyGeS-AM"

---

## 9. Phase 8 : Test et Vérification

### 9.1 Checklist d'Installation

| Élément | Statut | Action si problème |
|---------|--------|-------------------|
| Python installé | ☐ | Réinstaller Python |
| pip fonctionne | ☐ | `python -m pip install --upgrade pip` |
| SQL Server installé | ☐ | Vérifier dans Services |
| ODBC Driver installé | ☐ | Réinstaller le driver |
| Base de données créée | ☐ | Exécuter le script SQL |
| Django migrate | ☐ | `python manage.py migrate` |
| Superutilisateur créé | ☐ | `python manage.py createsuperuser` |
| Serveur accessible local | ☐ | Vérifier le pare-feu |
| Serveur accessible réseau | ☐ | Vérifier les règles de pare-feu |
| Page de connexion charge | ☐ | Vérifier les templates |
| Connexion admin fonctionne | ☐ | Vérifier les credentials |

### 9.2 Tests de Fonctionnalité

**Test 1 : Page d'accueil**

```
URL : http://192.168.1.100:8000
Attendu : Page d'accueil avec logo SyGeS-AM
```

**Test 2 : Connexion administrateur**

```
URL : http://192.168.1.100:8000/accounts/login/
Identifiant : admin
Mot de passe : (celui défini lors de createsuperuser)
Attendu : Redirection vers le tableau de bord
```

**Test 3 : Création d'un utilisateur**

```
Menu : Administration → Utilisateurs → Nouvel utilisateur
Créer un compte "secretaire"
Rôle : Secrétariat
Approuver le compte
```

**Test 4 : Connexion depuis un autre poste**

```
Depuis un PC client
Ouvrir : http://192.168.1.100:8000
Tester la connexion avec le compte "secretaire"
```

**Test 5 : Base de données SQL Server**

```sql
-- Exécuter dans SSMS depuis un poste distant
USE master;
GO
SELECT @@SERVERNAME;
GO

-- Vérifier les connexions actives
SELECT 
    s.login_name,
    s.host_name,
    s.program_name,
    s.login_time
FROM sys.dm_exec_sessions s
WHERE s.is_user_process = 1;
GO
```

### 9.3 Script de Vérification Automatique

Créer `verifier_installation.ps1` :

```powershell
# =============================================
# SCRIPT DE VÉRIFICATION - SYGeS-AM
# =============================================

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "VÉRIFICATION DE L'INSTALLATION SYGeS-AM" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$erreurs = 0

# 1. Vérifier Python
Write-Host "[1/10] Vérification de Python..." -NoNewline
try {
    $python = python --version 2>&1
    Write-Host " OK ($python)" -ForegroundColor Green
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    $erreurs++
}

# 2. Vérifier pip
Write-Host "[2/10] Vérification de pip..." -NoNewline
try {
    $pip = pip --version 2>&1 | Select-Object -First 1
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    $erreurs++
}

# 3. Vérifier SQL Server
Write-Host "[3/10] Vérification de SQL Server..." -NoNewline
$service = Get-Service -Name "MSSQL*" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host " OK ($($service.Name))" -ForegroundColor Green
} else {
    Write-Host " ERREUR - Service non trouvé" -ForegroundColor Red
    $erreurs++
}

# 4. Vérifier ODBC Driver
Write-Host "[4/10] Vérification du driver ODBC..." -NoNewline
$odbc = Get-OdbcDriver | Where-Object {$_.Name -like "*ODBC Driver 17*"}
if ($odbc) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " ERREUR - Driver non installé" -ForegroundColor Red
    $erreurs++
}

# 5. Vérifier la base de données
Write-Host "[5/10] Vérification de la base de données..." -NoNewline
try {
    $result = & sqlcmd -S localhost\SQLEXPRESS -d SyGeSAM_DB -Q "SELECT COUNT(*) as cnt FROM sys.tables" -h -1 -E 2>&1
    if ($result -match '\d+') {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " ERREUR" -ForegroundColor Red
        $erreurs++
    }
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    $erreurs++
}

# 6. Vérifier Django
Write-Host "[6/10] Vérification de Django..." -NoNewline
Set-Location C:\SyGeS-AM\gestion_ecole
try {
    $check = python manage.py check 2>&1
    if ($check -match "System check identified no issues") {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " AVERTISSEMENT" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    $erreurs++
}

# 7. Vérifier le port 8000
Write-Host "[7/10] Vérification du port 8000..." -NoNewline
$port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host " OK (En écoute)" -ForegroundColor Green
} else {
    Write-Host " AVERTISSEMENT - Serveur non démarré" -ForegroundColor Yellow
}

# 8. Vérifier le pare-feu
Write-Host "[8/10] Vérification du pare-feu..." -NoNewline
$fw = Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Django*"}
if ($fw) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " AVERTISSEMENT - Règle non créée" -ForegroundColor Yellow
}

# 9. Vérifier les fichiers statiques
Write-Host "[9/10] Vérification des fichiers statiques..." -NoNewline
if (Test-Path C:\SyGeS-AM\gestion_ecole\staticfiles) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " AVERTISSEMENT" -ForegroundColor Yellow
}

# 10. Vérification réseau
Write-Host "[10/10] Vérification de la connectivité réseau..." -NoNewline
$ip = Test-NetConnection -ComputerName 192.168.1.100 -WarningAction SilentlyContinue
if ($ip.PingSucceeded) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " AVERTISSEMENT" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
if ($erreurs -eq 0) {
    Write-Host "Installation réussie! L'application est prête." -ForegroundColor Green
} else {
    Write-Host "Installation terminée avec $erreurs erreur(s)." -ForegroundColor Yellow
}
Write-Host "Accédez à : http://192.168.1.100:8000" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
```

---

## 10. Annexes

### 10.1 Commandes CMD/Réseau Utiles

```cmd
# Information réseau
ipconfig /all

# Tester la connectivité
ping 192.168.1.100

# Vérifier les ports ouverts
netstat -an | findstr "1433 8000"

# Tester SQL Server à distance
sqlcmd -S 192.168.1.100\SQLEXPRESS -E

# Redémarrer SQL Server
net stop MSSQLSERVER && net start MSSQLSERVER

# Lister les services
sc query type= service state= all | findstr SQL

# Vérifier l'espace disque
wmic logicaldisk get size,freespace,caption
```

### 10.2 Commandes Django Utiles

```cmd
cd C:\SyGeS-AM\gestion_ecole

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Vérifier la configuration
python manage.py check

# Collecter les fichiers statiques
python manage.py collectstatic

# Démarrer le serveur
python manage.py runserver 0.0.0.0:8000

# Ouvrir le shell Django
python manage.py shell

# Lister les URLs
python manage.py show_urls
```

### 10.3 Fichier requirements.txt

```
# Créer ce fichier à la racine du projet

# Core Django
Django==5.0.4
djangorestframework==3.15.1
django-cors-headers==4.3.1

# Base de données
pyodbc==5.0.1
django-pyodbc-azure==2.1.0.0

# Sécurité
django-axes==6.0.0
django-simplejwt==5.3.1
cryptography==42.0.5

# PDF
reportlab==4.1.0

# Authentification 2FA
pyotp==2.9.0
qrcode==7.4.2
pillow==10.2.0

# Serveur
gunicorn==21.2.0
whitenoise==5.3.0

# Utilitaires
python-decouple==3.8
```

### 10.4 Dépannage Rapide

| Problème | Solution |
|----------|----------|
| "ODBC Driver not found" | Installer ODBC Driver 17 |
| "Connection refused" | Vérifier que Django est démarré |
| "Login failed" | Vérifier credentials SQL dans .env |
| "Network path not found" | Vérifier le pare-feu et IP |
| "Template not found" | Vérifier STATICFILES_DIRS |
| "Static files not loading" | Exécuter collectstatic |

### 10.5 Contacts Support

- **Développeur** : ANANI M. Prince
- **Email** : maounaananu0@gmail.com
- **WhatsApp** : +229 01 62 45 91 03 / +229 01 69 00 11 77

---

*Document généré pour le Système de Gestion Scolaire SyGeS-AM*
*Guide d'installation pour déploiement en réseau local avec SQL Server*
*Dernière mise à jour : Avril 2026*
*Version : 1.0*
