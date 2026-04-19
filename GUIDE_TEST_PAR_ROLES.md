# GUIDE DE TEST PAR RÔLES - Système de Gestion Scolaire SyGeS-AM

> Ce guide vous accompagne PAS À PAS pour tester toutes les fonctionnalités du système, **en passant par chaque rôle utilisateur** dans l'ordre chronologique d'une année scolaire.
> 
> **Important** : Ce guide ne concerne pas le Super Admin. Il est conçu pour tester le système avec les rôles opérationnels : Direction, Secrétariat, Comptabilité, Professeur et Surveillance.

---

## PRÉREQUIS AVANT TOUT TEST

### 1. Lancer le serveur
1. Ouvrir un terminal dans le dossier `gestion_ecole`
2. Exécuter : `python manage.py runserver`
3. Ouvrir votre navigateur à : **http://127.0.0.1:8000/**

### 2. Vérifier l'initialisation
Avant de commencer, assurez-vous que les modules sont créés :
```bash
python manage.py init_modules
```

---

## PHASE 1 : DIRECTION - Configuration Initiale

> **Rôle** : Direction  
> **Objectif** : Mettre en place la structure de l'année scolaire

### 1.1 Connexion en tant que Direction

1. Aller à : **http://127.0.0.1:8000/**
2. Se connecter avec les identifiants Direction :
   - **Nom d'utilisateur** : `direction1` (ou créer un utilisateur avec rôle `direction`)
   - **Mot de passe** : selon ce qui a été défini
3. Vérifier que le tableau de bord Direction s'affiche

### 1.2 Créer l'Année Scolaire

**Chemin** : **Configuration** → **Années scolaires** → **[Ajouter]**

1. **Libellé** : `2025-2026`
2. **Date de début** : `2025-09-01`
3. **Date de fin** : `2026-07-31`
4. **Est active** : ☑ Cocher
5. Cliquer sur **[Enregistrer]**

**Vérifier** : L'année apparaît avec le statut "Active"

### 1.3 Créer les Cycles

**Chemin** : **Finances** → **Cycles** → **[Ajouter]**

Créer les cycles pédagogiques :

| Type | Nom | Description |
|------|-----|-------------|
| 1 | `Premier Cycle` | 6ème à 3ème (Collège) |
| 2 | `Second Cycle` | 2nde à Terminale (Lycée) |

### 1.4 Créer les Niveaux Scolaires

**Chemin** : **Core** → **Niveaux scolaires** → **[Ajouter]**

Créer dans l'ordre :

| Ordre | Nom | Cycle |
|-------|-----|-------|
| 1 | `6ème` | Premier Cycle |
| 2 | `5ème` | Premier Cycle |
| 3 | `4ème` | Premier Cycle |
| 4 | `3ème` | Premier Cycle |

### 1.5 Créer les Périodes d'Évaluation

**Chemin** : **Core** → **Périodes d'évaluation** → **[Ajouter]**

Créer les trimestres :

| Nom | Date début | Date fin | Ordre |
|-----|------------|----------|-------|
| `Trimestre 1` | 2025-09-01 | 2025-12-20 | 1 |
| `Trimestre 2` | 2026-01-05 | 2026-03-31 | 2 |
| `Trimestre 3` | 2026-04-01 | 2026-07-15 | 3 |

### 1.6 Créer les Classes

**Chemin** : **Enseignement** → **Classes** → **[Ajouter]**

Créer les classes :

| Nom | Niveau | Effectif max |
|-----|--------|--------------|
| `6ème A` | 6ème | 30 |
| `6ème B` | 6ème | 30 |
| `5ème A` | 5ème | 30 |
| `4ème A` | 4ème | 25 |
| `3ème A` | 3ème | 25 |

### 1.7 Créer les Matières

**Chemin** : **Enseignement** → **Matières** → **[Ajouter]**

| Nom | Code | Coefficient |
|-----|------|-------------|
| `Mathématiques` | MATH | 4 |
| `Français` | FR | 4 |
| `Anglais` | ANG | 3 |
| `Histoire-Géographie` | HG | 2 |
| `Sciences Naturelles` | SVT | 2 |
| `Physique-Chimie` | PC | 2 |
| `EPS` | EPS | 2 |

### 1.8 Créer les Utilisateurs des Autres Rôles

**Chemin** : **Administration** → **Utilisateurs** → **[Ajouter]**

Créer les comptes pour les autres rôles :

#### Secrétaire
- **Nom d'utilisateur** : `secretaire1`
- **Email** : `secretaire@ecole.fr`
- **Mot de passe** : `Secretaire2026!`
- **Rôle** : `secretaire`
- **Est approuvé** : ☑ Cocher

#### Comptable
- **Nom d'utilisateur** : `comptable1`
- **Email** : `comptable@ecole.fr`
- **Mot de passe** : `Comptable2026!`
- **Rôle** : `comptable`
- **Est approuvé** : ☑ Cocher

#### Professeur (Mathématiques)
- **Nom d'utilisateur** : `prof_math`
- **Email** : `prof.math@ecole.fr`
- **Mot de passe** : `Prof2026!`
- **Rôle** : `professeur`
- **Est approuvé** : ☑ Cocher

#### Professeur (Français)
- **Nom d'utilisateur** : `prof_fr`
- **Email** : `prof.fr@ecole.fr`
- **Mot de passe** : `Prof2026!`
- **Rôle** : `professeur`
- **Est approuvé** : ☑ Cocher

#### Surveillance
- **Nom d'utilisateur** : `surveillant1`
- **Email** : `surveille@ecole.fr`
- **Mot de passe** : `Surveille2026!`
- **Rôle** : `surveillance`
- **Est approuvé** : ☑ Cocher

### 1.9 Créer les Profils Professeurs

**Chemin** : **Enseignement** → **Professeurs** → **[Ajouter]**

1. **Professeur Mathématiques** :
   - **Utilisateur** : `prof_math`
   - **Spécialité** : Mathématiques
   - **Grade** : `Professeur Certifié`

2. **Professeur Français** :
   - **Utilisateur** : `prof_fr`
   - **Spécialité** : Français
   - **Grade** : `Professeur Certifié`

### 1.10 Créer les Attributions

**Chemin** : **Enseignement** → **Attributions** → **[Ajouter]**

| Professeur | Matière | Classe | Année |
|------------|---------|--------|-------|
| `prof_math` | Mathématiques | 6ème A | 2025-2026 |
| `prof_math` | Mathématiques | 6ème B | 2025-2026 |
| `prof_fr` | Français | 6ème A | 2025-2026 |
| `prof_fr` | Français | 5ème A | 2025-2026 |

---

## PHASE 2 : SECRÉTARIAT - Gestion des Élèves

> **Rôle** : Secrétaire  
> **Objectif** : Enregistrer les élèves et gérer les inscriptions

### 2.1 Connexion en tant que Secrétaire

1. Se déconnecter (clic sur nom en haut à droite → Déconnexion)
2. Se connecter avec :
   - **Nom d'utilisateur** : `secretaire1`
   - **Mot de passe** : `Secretaire2026!`
3. Vérifier que seuls les modules autorisés apparaissent :
   - Scolarité (Élèves, Inscriptions, Discipline)
   - Enseignement (Classes, Professeurs, Matières - Lecture seule)
   - Rapports (Bulletins, Fiches de notes)

### 2.2 Enregistrer les Élèves

**Chemin** : **Scolarité** → **Élèves** → **[Ajouter]**

Créer 5 élèves minimum :

#### Élève 1
- **Nom** : `KAMGA`
- **Prénom** : `Marie`
- **Date naissance** : `2014-03-15`
- **Sexe** : Féminin
- **Lieu naissance** : Yaoundé

#### Élève 2
- **Nom** : `TCHOUAMO`
- **Prénom** : `Jean-Paul`
- **Date naissance** : `2013-08-22`
- **Sexe** : Masculin
- **Lieu naissance** : Douala

#### Élève 3
- **Nom** : `ESSOUMA`
- **Prénom** : `Sophie`
- **Date naissance** : `2014-01-10`
- **Sexe** : Féminin
- **Lieu naissance** : Bafoussam

#### Élève 4
- **Nom** : `MBOUDA`
- **Prénom** : `Luc`
- **Date naissance** : `2013-11-05`
- **Sexe** : Masculin
- **Lieu naissance** : Yaoundé

#### Élève 5
- **Nom** : `NGOUM`
- **Prénom** : `Chantal`
- **Date naissance** : `2014-06-18`
- **Sexe** : Féminin
- **Lieu naissance** : Garoua

**Vérifier** : Les matricules sont générés automatiquement (ex: ELV-2025-001)

### 2.3 Inscrire les Élèves

**Chemin** : **Scolarité** → **Inscriptions** → **[Ajouter]**

| Élève | Classe | Date inscription | Statut |
|-------|--------|------------------|--------|
| KAMGA Marie | 6ème A | 2025-09-02 | Actif |
| TCHOUAMO Jean-Paul | 6ème A | 2025-09-02 | Actif |
| ESSOUMA Sophie | 6ème A | 2025-09-03 | Actif |
| MBOUDA Luc | 6ème B | 2025-09-03 | Actif |
| NGOUM Chantal | 5ème A | 2025-09-04 | Actif |

### 2.4 Ajouter des Parents/Tuteurs

**Chemin** : **Scolarité** → **Élèves** → Cliquer sur un élève → Onglet **Parents**

Pour KAMGA Marie :
- **Nom** : `KAMGA`
- **Prénom** : `Martine`
- **Téléphone** : 699123456
- **Email** : parent1@email.com
- **Lien** : Mère

### 2.5 Gérer les Dossiers Médicaux

**Chemin** : **Scolarité** → **Dossiers médicaux**

Pour TCHOUAMO Jean-Paul :
- **Groupe sanguin** : O+
- **Allergies** : Aucune
- **Maladies chroniques** : Aucune

### 2.6 Test des Documents des Élèves

**Chemin** : **Scolarité** → **Documents**

1. Cliquer sur **[Ajouter un document]**
2. Sélectionner l'élève KAMGA Marie
3. **Type** : Certificat de naissance
4. **Fichier** : Sélectionner un fichier PDF de test
5. Cliquer sur **[Enregistrer]**

---

## PHASE 3 : COMPTABILITÉ - Gestion Financière

> **Rôle** : Comptable  
> **Objectif** : Configurer les frais et suivre les paiements

### 3.1 Connexion en tant que Comptable

1. Se déconnecter
2. Se connecter avec :
   - **Nom d'utilisateur** : `comptable1`
   - **Mot de passe** : `Comptable2026!`
3. Vérifier les modules accessibles :
   - Finances (Frais, Paiements, Caisse, Charges, Rapports)
   - Scolarité (Élèves, Inscriptions - Lecture seule)
   - Rapports (Statistiques globales)

### 3.2 Créer les Frais Scolaires

**Chemin** : **Finances** → **Frais scolaires** → **[Ajouter]**

| Libellé | Montant | Classe | Échéance |
|---------|---------|--------|----------|
| `Frais 6ème 2025-2026` | 50000 | 6ème A | 2025-09-30 |
| `Frais 6ème 2025-2026` | 50000 | 6ème B | 2025-09-30 |
| `Frais 5ème 2025-2026` | 55000 | 5ème A | 2025-09-30 |

### 3.3 Enregistrer des Paiements

**Chemin** : **Finances** → **Paiements** → **[Ajouter]**

| Élève | Montant | Date | Mode | Référence |
|-------|---------|------|------|----------|
| KAMGA Marie | 50000 | 2025-09-10 | Espèces | PAI-001 |
| TCHOUAMO Jean-Paul | 25000 | 2025-09-12 | Virement | PAI-002 |
| ESSOUMA Sophie | 50000 | 2025-09-15 | Espèces | PAI-003 |

### 3.4 Gérer la Caisse

**Chemin** : **Finances** → **Caisse**

1. **Ouvrir la caisse** :
   - Montant initial : `100000`
   - Cliquer **[Ouvrir]**

2. **Enregistrer une opération** :
   - Type : Encaissement
   - Montant : 50000
   - Description : Paiement frais scolarité - KAMGA Marie
   - Date : 2025-09-10

3. **Vérifier le solde** : Doit afficher 150000 FCFA

### 3.5 Créer les Charges

**Chemin** : **Finances** → **Charges**

#### Charge Fixe
- **Libellé** : Loyer bâtiment scolaire
- **Montant** : 300000
- **Fréquence** : Mensuelle
- **Date début** : 2025-09-01

#### Charge Opérationnelle
- **Libellé** : Achat fournitures bureau
- **Montant** : 50000
- **Date** : 2025-09-15
- **Catégorie** : Fournitures

### 3.6 Générer des Factures

**Chemin** : **Finances** → **Factures**

1. Sélectionner l'élève : TCHOUAMO Jean-Paul
2. Cliquer **[Générer la facture]**
3. Vérifier que la facture PDF se télécharge avec :
   - Montant total : 50000
   - Montant payé : 25000
   - Reste à payer : 25000

### 3.7 Consulter le Tableau de Bord Financier

**Chemin** : **Finances** → **Tableau de bord**

Vérifier l'affichage de :
- Total frais scolarité attendu
- Total encaissé
- Taux de recouvrement
- Graphiques mensuels

---

## PHASE 4 : PROFESSEUR - Enseignement et Évaluations

> **Rôle** : Professeur  
> **Objectif** : Saisir les notes et gérer les présences

### 4.1 Connexion Professeur Mathématiques

1. Se déconnecter
2. Se connecter avec :
   - **Nom d'utilisateur** : `prof_math`
   - **Mot de passe** : `Prof2026!`
3. Vérifier les modules accessibles :
   - Mes Classes
   - Mes Séances
   - Saisie des notes
   - Emploi du temps

### 4.2 Voir "Mes Classes"

**Chemin** : **Espace Enseignant** → **Mes Classes**

Vérifier l'affichage de :
- 6ème A (Mathématiques)
- 6ème B (Mathématiques)

### 4.3 Créer une Séance de Cours

**Chemin** : **Espace Enseignant** → **Mes Séances** → **[Créer]**

1. **Classe** : 6ème A
2. **Matière** : Mathématiques
3. **Date** : 2025-10-15
4. **Heure début** : 08:00
5. **Durée** : 60 minutes
6. Cliquer **[Enregistrer]**

### 4.4 Effectuer l'Appel

1. Après création de la séance, cliquer **[Faire l'appel]**
2. Pour chaque élève, sélectionner :
   - KAMGA Marie : **Présent** (bouton vert)
   - TCHOUAMO Jean-Paul : **Présent**
   - ESSOUMA Sophie : **Absent** (bouton rouge) → Motif : Maladie
3. Cliquer **[Valider l'appel]**

### 4.5 Créer un Examen

**Chemin** : **Enseignement** → **Examens** → **[Créer]**

1. **Titre** : Devoir surveillé n°1
2. **Classe** : 6ème A
3. **Matière** : Mathématiques
4. **Période** : Trimestre 1
5. **Date** : 2025-10-20
6. **Coefficient** : 1
7. **Durée** : 60 minutes
8. Cliquer **[Enregistrer]**

### 4.6 Saisir les Notes

**Chemin** : **Enseignement** → **Examens** → Cliquer sur l'examen

1. Dans la grille, saisir les notes :
   - KAMGA Marie : 15/20
   - TCHOUAMO Jean-Paul : 12/20
   - ESSOUMA Sophie : (laisser vide - était absente)
2. Cliquer **[Enregistrer les notes]**

### 4.7 Consulter les Fiches de Notes

**Chemin** : **Rapports** → **Fiches de notes**

1. Sélectionner :
   - Classe : 6ème A
   - Matière : Mathématiques
   - Période : Trimestre 1
2. Cliquer **[Générer]**
3. Vérifier que les notes apparaissent correctement

### 4.8 Se connecter en tant que Professeur Français

1. Se déconnecter
2. Se connecter avec `prof_fr` / `Prof2026!`
3. Répéter les étapes 4.5 à 4.7 pour la matière Français

---

## PHASE 5 : SURVEILLANCE - Contrôle et Discipline

> **Rôle** : Surveillance  
> **Objectif** : Gérer les présences globales et la discipline

### 5.1 Connexion Surveillant

1. Se déconnecter
2. Se connecter avec :
   - **Nom d'utilisateur** : `surveillant1`
   - **Mot de passe** : `Surveille2026!`
3. Vérifier les modules accessibles :
   - Présences (Appel, Statistiques, Rapport retards)
   - Scolarité (Élèves - Lecture, Discipline)

### 5.2 Voir les Statistiques de Présence

**Chemin** : **Présences** → **Statistiques**

1. Sélectionner la période : 2025-09-01 à 2025-10-31
2. Vérifier les taux de présence par classe
3. Exporter en PDF si nécessaire

### 5.3 Consulter le Rapport des Retards

**Chemin** : **Présences** → **Rapport retards**

Vérifier l'affichage des :
- Élèves avec retards cumulés
- Statistiques par classe
- Graphiques de fréquentation

### 5.4 Gérer la Discipline

**Chemin** : **Scolarité** → **Sanctions & Récompenses**

#### Créer une Sanction
1. **[Ajouter]**
2. **Élève** : MBOUDA Luc
3. **Type** : Sanction
4. **Motif** : Retard répété
5. **Date** : 2025-10-10
6. **Gravité** : Mineure
7. **Description** : 3 retards en une semaine
8. **[Enregistrer]**

#### Créer une Récompense
1. **[Ajouter]**
2. **Élève** : KAMGA Marie
3. **Type** : Récompense
4. **Motif** : Excellence scolaire
5. **Date** : 2025-10-12
6. **Gravité** : Excellence
7. **Description** : Majorante en Mathématiques
8. **[Enregistrer]**

### 5.5 Effectuer un Appel en Surveillance

**Chemin** : **Présences** → **Appel** → **[Créer une séance]**

1. **Classe** : 5ème A
2. **Matière** : (laisser vide ou Séance de surveillance)
3. **Date** : Date du jour
4. **Heure** : 10:00
5. **[Démarrer]**
6. Faire l'appel pour tous les élèves présents
7. **[Valider]**

---

## PHASE 6 : DIRECTION - Validation et Rapports

> **Rôle** : Direction  
> **Objectif** : Clôturer les périodes et générer les rapports

### 6.1 Connexion Direction

1. Se déconnecter
2. Se reconnecter avec `direction1`

### 6.2 Clôturer la Période d'Évaluation

**Chemin** : **Scolarité** → **Clôture des périodes**

1. Sélectionner **Trimestre 1**
2. Vérifier que toutes les notes sont saisies
3. Cliquer **[Clôturer la période]**
4. Confirmer la clôture

**Vérifier** : Un message confirme que la clôture est effective

### 6.3 Générer les Bulletins

**Chemin** : **Rapports** → **Bulletins** → **[Générer]**

#### Bulletin Individuel
1. **Élève** : KAMGA Marie
2. **Classe** : 6ème A
3. **Période** : Trimestre 1
4. Cliquer **[Générer le bulletin]**
5. Vérifier le PDF téléchargé contient :
   - Notes de Mathématiques : 15/20
   - Notes de Français : (selon saisie)
   - Moyenne générale calculée

#### Bulletins par Classe
1. Sélectionner **6ème A**
2. Sélectionner **Trimestre 1**
3. Cliquer **[Générer tous les bulletins]**

### 6.4 Générer le Rapport Financier

**Chemin** : **Rapports** → **Rapport financier**

1. Sélectionner la période : **Trimestre 1**
2. Cliquer **[Générer]**
3. Vérifier l'affichage de :
   - Total encaissements
   - Total dépenses
   - Solde de la période
   - Graphiques

### 6.5 Consulter les Statistiques Globales

**Chemin** : **Rapports** → **Statistiques globales**

Vérifier :
- Nombre total d'élèves par classe
- Taux de présence global
- Répartition par sexe
- Performance académique moyenne

### 6.6 Gérer les Approbations (si nécessaire)

**Chemin** : **Administration** → **Approbations**

Vérifier s'il y a des demandes en attente :
- Nouveaux utilisateurs à approuver
- Demandes de modification

---

## PHASE 7 : Tests Transversaux par Rôle

### 7.1 Test des Permissions - Vérifier l'Isolation des Rôles

#### Test Comptable - Accès Interdit
1. Se connecter en tant que `comptable1`
2. Tenter d'accéder à **Scolarité** → **Inscriptions**
   - Résultat attendu : Lecture seule autorisée
3. Tenter de créer un élève
   - Résultat attendu : Message "Vous n'avez pas l'autorisation"

#### Test Professeur - Accès Limité
1. Se connecter en tant que `prof_math`
2. Vérifier que **Finances** n'apparaît pas dans le menu
3. Vérifier que seules ses classes (6ème A, 6ème B) sont visibles

#### Test Secrétaire - Accès Complet Scolarité
1. Se connecter en tant que `secretaire1`
2. Vérifier l'accès à :
   - Élèves (CRUD complet)
   - Inscriptions (CRUD complet)
   - Discipline (CRUD complet)
3. Vérifier que **Finances** n'est pas accessible

### 7.2 Test des Notifications

**Chemin** : **Communication** → **Notifications**

1. Direction envoie une notification :
   - Destinataires : Tous les professeurs
   - Message : "Réunion pédagogique le 15/11 à 14h"
2. Se connecter en tant que `prof_math`
3. Cliquer sur l'icône **cloche** en haut
4. Vérifier que la notification est reçue

---

## CHECKLIST FINALE DE VALIDATION

| # | Test | Rôle | Résultat Attendu | ✓ |
|---|------|------|------------------|---|
| 1 | Création année scolaire | Direction | Année 2025-2026 active | ☐ |
| 2 | Création classes | Direction | 5 classes créées | ☐ |
| 3 | Création matières | Direction | 7 matières créées | ☐ |
| 4 | Création utilisateurs | Direction | 5 utilisateurs créés | ☐ |
| 5 | Création profils professeurs | Direction | 2 professeurs liés | ☐ |
| 6 | Création attributions | Direction | 4 attributions actives | ☐ |
| 7 | Enregistrement élèves | Secrétaire | 5 élèves créés avec matricule | ☐ |
| 8 | Inscription élèves | Secrétaire | 5 inscriptions actives | ☐ |
| 9 | Ajout parents | Secrétaire | Parents liés aux élèves | ☐ |
| 10 | Dossiers médicaux | Secrétaire | Informations médicales enregistrées | ☐ |
| 11 | Création frais | Comptable | 3 types de frais créés | ☐ |
| 12 | Enregistrement paiements | Comptable | 3 paiements enregistrés | ☐ |
| 13 | Gestion caisse | Comptable | Solde correctement calculé | ☐ |
| 14 | Création charges | Comptable | 2 charges enregistrées | ☐ |
| 15 | Génération factures | Comptable | PDF généré avec détails | ☐ |
| 16 | Tableau bord financier | Comptable | Graphiques affichés | ☐ |
| 17 | Voir mes classes | Professeur | Classes attribuées visibles | ☐ |
| 18 | Créer séance | Professeur | Séance créée avec succès | ☐ |
| 19 | Effectuer appel | Professeur | Présences enregistrées | ☐ |
| 20 | Créer examen | Professeur | Examen planifié | ☐ |
| 21 | Saisir notes | Professeur | Notes enregistrées | ☐ |
| 22 | Fiches de notes | Professeur | Moyennes calculées | ☐ |
| 23 | Statistiques présences | Surveillance | Taux de présence visibles | ☐ |
| 24 | Rapport retards | Surveillance | Liste des retards affichée | ☐ |
| 25 | Gestion discipline | Surveillance | Sanctions/récompenses créées | ☐ |
| 26 | Clôturer période | Direction | Période verrouillée | ☐ |
| 27 | Générer bulletins | Direction | PDFs générés | ☐ |
| 28 | Rapport financier | Direction | Bilan financier affiché | ☐ |
| 29 | Stats globales | Direction | Statistiques globales visibles | ☐ |
| 30 | Isolation rôles | Tous | Accès limités selon rôle | ☐ |

---

## RÉCAPITULATIF DES RÔLES ET ACCÈS

| Rôle | Modules Accès | Actions Principales |
|------|---------------|---------------------|
| **Direction** | Tous les modules | Configuration, validation, rapports |
| **Secrétaire** | Scolarité (CRUD), Enseignement (Lecture), Rapports (Lecture) | Inscriptions, élèves, discipline |
| **Comptable** | Finances (CRUD), Scolarité (Lecture), Rapports (Lecture) | Paiements, caisse, charges |
| **Professeur** | Espace Enseignant, Présences (ses séances), Notes | Saisie notes, appel, séances |
| **Surveillance** | Présences (CRUD), Discipline (CRUD), Élèves (Lecture) | Appel, discipline, statistiques |

---

## EN CAS DE PROBLÈME

### Accès refusé à un module
1. Vérifier que le rôle de l'utilisateur est correctement défini
2. Vérifier que les modules sont activés dans **Administration** → **Permissions**
3. Réinitialiser les permissions : `python manage.py init_modules`

### Module non visible dans le menu
1. Vérifier que le module est actif dans la base de données
2. Vérifier les permissions du rôle dans `init_modules.py`

### Erreur lors de la génération de bulletin
1. Vérifier que la période est clôturée
2. Vérifier que toutes les notes sont saisies
3. Vérifier que l'élève est inscrit dans une classe

---

*Dernière mise à jour : 19 Avril 2026*  
*Version : 2.1 - SyGeS-AM - Guide par Rôles*
