# Système de Gestion Scolaire - Django

## Structure du Projet

```
gestion_ecole/
├── core/                  # Configuration Django principale
│   ├── settings.py        # Paramètres de l'application
│   ├── urls.py            # URLs principales
│   ├── middleware.py      # Middleware personnalisé
│   └── context_processors.py
├── accounts/              # Gestion des utilisateurs
│   ├── models.py          # User personnalisé + logs
│   ├── views.py           # Login/Logout/Profile
│   └── urls.py
├── eleves/                # Gestion des élèves
│   ├── models.py          # Eleve, Inscription
│   ├── views.py           # CRUD élèves
│   └── forms.py
├── academics/             # Gestion académique
│   ├── models.py          # Classe, Matiere, Professeur, Evaluation
│   ├── views.py           # Saisie notes, attributions
│   └── forms.py
├── presences/             # Gestion des présences
│   ├── models.py          # Presence, Appel
│   ├── views.py           # Appel, statistiques
│   └── forms.py
├── finances/             # Gestion financière
│   ├── models.py          # AnneeScolaire, Frais, Paiement, Salaire
│   ├── views.py           # Paiements, salaires, rappels
│   └── forms.py
├── rapports/             # Rapports et bulletins
│   ├── models.py          # Bulletin
│   ├── views.py           # Génération PDF
│   └── forms.py
├── templates/             # Templates HTML Bootstrap
└── manage.py
```

## Installation

### 1. Prérequis
- Python 3.11+
- SQL Server Express (optionnel, sinon SQLite)
- pip

### 2. Créer l'environnement virtuel
```bash
cd gestion_ecole
python -m venv venv
.\venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données

#### Option A: SQLite (développement rapide)
Aucune configuration nécessaire, fonctionne par défaut.

#### Option B: SQL Server Express
1. Installer SQL Server Express
2. Activer l'authentification SQL
3. Créer la base de données `GestionEcole`
4. Modifier `.env` avec vos identifiants
5. Modifier `settings.py` (voir `SQL_SERVER_CONFIG.py`)

### 5. Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un super utilisateur
```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur
```bash
python manage.py runserver
```

## Utilisation

1. Accéder à `http://localhost:8000/admin/` pour l'administration
2. Créer une année scolaire active
3. Créer les utilisateurs avec leurs rôles
4. Configurer les classes, matières, frais
5. Insrire les élèves

## Rôles disponibles

| Rôle | Droits |
|------|--------|
| Direction | Accès total |
| Secrétariat | Élèves, classes, bulletins |
| Comptabilité | Finances, paiements, salaires |
| Professeur | Ses classes, notes, présences |
| Surveillance | Présences uniquement |

## Commandes utiles

```bash
# Développement
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic
```
