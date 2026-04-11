# Système de Gestion Scolaire SyGeS-AM (V2)

Système de gestion d'établissement scolaire complet (Maternelle, Primaire, Secondaire, Supérieur) développé avec **Django 5.0** et **PostgreSQL**.

## 🚀 Fonctionnalités Clés

- **Authentification Sécurisée** : Rôles personnalisés, 2FA (TOTP), Journal d'audit complet.
- **Scolarité** : Inscriptions, Dossiers médicaux, Suivi disciplinaire (Sanctions/Récompenses).
- **Enseignement** : Classes, Matières, Profils Professeurs, Attributions, Examens et Notes.
- **Présences** : Appels numériques par séance, statistiques d'assiduité.
- **Finances** : Frais scolaires, Paiements, Opérations de caisse, Charges et Salaires.
- **Rapports** : Génération de bulletins PDF et rapports financiers.
- **API REST** : Architecture prête pour mobile/SPA avec Django REST Framework.

## 📁 Structure du Projet (Refonte V2)

```
gestion_ecole/
├── core/                  # Configuration principale, Années scolaires, Cycles
├── authentification/      # Utilisateurs, Rôles, 2FA, Audit (Ancien accounts)
├── scolarite/             # Élèves, Inscriptions, Discipline (Ancien eleves)
├── enseignement/          # Classes, Matières, Notes, Examens (Ancien academics)
├── ressources_humaines/   # Personnel, Salaires, Contrats (Nouveau)
├── presences/             # Appels, Séances de cours
├── finances/              # Frais, Paiements, Caisse, Charges
├── rapports/              # Bulletins PDF, Statistiques
├── templates/             # Templates HTML (Bootstrap 5)
└── manage.py
```

## 🛠️ Installation Rapide

### 1. Prérequis
- Python 3.11+
- PostgreSQL 15+
- pip

### 2. Environnement Virtuel
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration Base de Données
1. Créer une base PostgreSQL nommée `gestion_scolaire`.
2. Mettre à jour les identifiants dans `core/settings.py`.

### 4. Initialisation
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_modules
python manage.py createsuperuser
```

### 5. Lancer le serveur
```bash
python manage.py runserver
```

## 📚 Documentation Complète

- [Architecture Détaillée](ARCHITECTURE.md)
- [Guide d'Installation Réseau](GUIDE_INSTALLATION.md)
- [Manuel d'Utilisation](MANUEL_UTILISATION.md)
- [Guide Complet de Test](GUIDE_TEST_COMPLET.md)

---
*Dernière mise à jour : 11 Avril 2026*
*Version : 2.0*
