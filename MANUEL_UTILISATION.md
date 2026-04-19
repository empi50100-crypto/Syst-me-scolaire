# Manuel d'Utilisation - Système de Gestion Scolaire SyGeS-AM

> Ce manuel est un guide complet pour l'utilisation quotidienne du système.
> Chaque section indique : pourquoi faire une action, comment la réaliser, et quid vérifier.
>
> **📘 Guide de Test** : Pour tester le système avec différents rôles (Direction, Secrétariat, Comptable, Professeur, Surveillance), consultez le **[Guide de Test par Rôles](GUIDE_TEST_PAR_ROLES.md)**.

---

## TABLE DES MATIÈRES

1. [Connexion et Premiers Pas](#1-connexion-et-premiers-pas)
2. [Configuration de l'Année Scolaire](#2-configuration-de-lannée-scolaire)
3. [ Gestion des Utilisateurs](#3-gestion-des-utilisateurs)
4. [Organisation Académique](#4-organisation-académique)
5. [Gestion des Élèves](#5-gestion-des-élèves)
6. [Suivi des Présences](#6-suivi-des-présences)
7. [Évaluations et Notes](#7-évaluations-et-notes)
8. [Finances et Comptabilité](#8-finances-et-comptabilité)
9. [Ressources Humaines](#9-ressources-humaines)
10. [Rapports et Bulletins](#10-rapports-et-bulletins)
11. [Communication Interne](#11-communication-interne)
12. [Rôles et Permissions](#12-rôles-et-permissions)
13. [Dépannage](#13-dépannage)

---

## 1. CONNEXION ET PREMIERS PAS

### 1.1 Se connecter au système
**Pourquoi** : Pour accéder aux fonctionnalités du système, vous devez d'abord vous authentifier.

**Étapes** :
1. Ouvrir votre navigateur web (Chrome, Firefox, Edge)
2. Dans la barre d'adresse, saisir : **`http://127.0.0.1:8000/`**
3. La page de connexion s'affiche automatiquement
4. Dans le champ **Nom d'utilisateur**, saisir votre identifiant (ex: `admin`)
5. Dans le champ **Mot de passe**, saisir votre mot de passe
6. Cliquer sur **[Se connecter]** ou appuyez sur la touche `Entrée`

**Vérifier** :
- Si les identifiants sont corrects, vous êtes redirigé vers le **Tableau de bord**
- Si les identifiants sont incorrects, un message d'erreur s'affiche

### 1.2 Naviguer dans l'interface
**Pourquoi** : Le système possède un menu latéral pour accéder à toutes les fonctionnalités.

**Le menu latéral (sidebar)** :
- Located à **gauche de l'écran**
- Contient des **groupes de services** dépliables :
  - **Tableau de bord** : Accueil
  - **Core** : Configuration globale
  - **Authentification** : Gestion des utilisateurs
  - **Scolarité** : Gestion des élèves
  - **Enseignement** : Cours et notes
  - **Présences** : Suivi des absences
  - **Finances** : Paiements et comptabilité
  - **Ressources Humaines** : Personnel
  - **Rapports** : Bulletins et statistiques

**Comment naviguer** :
1. Cliquer sur le **triangle ▶** à côté d'un service pour déplier les modules
2. Cliquer sur le **nom d'un module** pour y accéder
3. Le module actif est affiché avec un **fond de couleur différente**

### 1.3 Se déconnecter
**Pourquoi** : Pour sécuriser votre session lorsque vous quittez l'ordinateur.

**Étapes** :
1. Cliquer sur votre **nom d'utilisateur** en haut à droite
2. Dans le menu déroulant, cliquer sur **[Déconnexion]**

---

## 2. CONFIGURATION DE L'ANNÉE SCOLAIRE

### 2.1 Créer une année scolaire
**Pourquoi** : Sans année scolaire active, aucune inscription ni opération n'est possible.

**Cheminement** : **Core** → **Années scolaires** → **[Ajouter]**

**Étapes** :
1. Dans le champ **Libellé**, saisir le nom (ex: `2025-2026`)
2. Dans **Date de début**, sélectionner le 1er septembre de l'année
3. Dans **Date de fin**, sélectionner le 31 juillet de l'année suivante
4. **Cocher la case "Est active"** pour rendre cette année utilisable
5. Cliquer sur **[Enregistrer]**

**Vérifier** : L'année apparaît dans la liste avec un indicateur "Active"

### 2.2 Créer des cycles scolaires
**Pourquoi** : Les cycles organize les niveaux pédagogiques (Maternelle, Primaire, Collège, etc.)

**Cheminement** : **Core** → **Cycles** → **[Ajouter]**

**Étapes** :
1. Dans **Nom**, saisir le nom du cycle (ex: `Primaire`)
2. Dans **Code**, saisir un code court (ex: `primaire`)
3. Cliquer sur **[Enregistrer]**

**Exemples de cycles à créer** :
- Maternelle, Primaire, Collège, Lycée

### 2.3 Créer des niveaux scolaires
**Pourquoi** : Les niveaux définissent les classes (6ème, 5ème, etc.)

**Cheminement** : **Core** → **Niveaux scolaires** → **[Ajouter]**

**Étapes** :
1. Dans **Nom**, saisir le nom (ex: `6ème`)
2. Dans **Ordre**, saisir un numéro (1 pour le plus bas, 4 pour 3ème)
3. Dans **Cycle**, sélectionner le cycle correspondant
4. Cliquer sur **[Enregistrer]**

### 2.4 Créer des périodes d'évaluation
**Pourquoi** : Pour définir les périodes de notation (trimestres/semestres)

**Cheminement** : **Core** → **Périodes d'évaluation** → **[Ajouter]**

**Étapes** :
1. Dans **Nom**, saisir (ex: `Trimestre 1`)
2. Dans **Date de début**, sélectionner la date de début
3. Dans **Date de fin**, sélectionner la date de fin
4. Dans **Ordre**, saisir le numéro du trimestre
5. Cliquer sur **[Enregistrer]**

---

## 3. GESTION DES UTILISATEURS

### 3.1 Créer un nouvel utilisateur
**Pourquoi** : Chaque membre du personnel doit avoir un compte pour accéder au système.

**Cheminement** : **Authentification** → **Utilisateurs** → **[Ajouter un utilisateur]**

**Étapes** :
1. **Nom d'utilisateur** : Saisir un identifiant unique
2. **Adresse email** : Saisir l'email professionnel
3. **Mot de passe** : Saisir un mot de passe robuste
4. **Confirmer le mot de passe** : Le resaisir
5. **Prénom** : Saisir le prénom
6. **Nom** : Saisir le nom de famille
7. **Rôle** : Sélectionner le rôle dans la liste :
   - `superadmin` = Super Administrateur
   - `direction` = Direction
   - `secretaire` = Secrétariat
   - `comptable` = Comptabilité
   - `professeur` = Enseignement
   - `surveillance` = Contrôle & Surveillance
8. **Est approuvé** : ☑ Cocher pour autoriser la connexion
9. Cliquer sur **[Enregistrer]**

**Vérifier** : Le nouvel utilisateur apparaît dans la liste et peut se connecter

### 3.2 Modifier un utilisateur
**Cheminement** : **Authentification** → **Utilisateurs** → Cliquer sur l'utilisateur

**Étapes** :
1. Modifier les champs souhaités
2. Cliquer sur **[Enregistrer]**

### 3.3 Désactiver un compte utilisateur
**Pourquoi** : Pour empêche un utilisateur de se connecter temporairement.

**Étapes** :
1. Ouvrir le profil de l'utilisateur
2. **Décocher la case "Est actif"**
3. Cliquer sur **[Enregistrer]**

### 3.4 Consulter le journal d'audit
**Pourquoi** : Pour tracer toutes les actions des utilisateurs.

**Cheminement** : **Authentification** → **Journal d'audit**

** Fonctionnalités** :
- Voir qui a fait quelle action
- Filtrer par date, utilisateur, type d'action

---

## 4. ORGANISATION ACADÉMIQUE

### 4.1 Créer une classe
**Pourquoi** : Une classe regroupe les élèves pour un niveau donné.

**Cheminement** : **Enseignement** → **Classes** → **[Ajouter une classe]**

**Étapes** :
1. **Nom** : Saisir le nom (ex: `6ème A`)
2. **Niveau** : Sélectionner le niveau (`6ème`)
3. **Année scolaire** : Sélectionner l'année active
4. **Effectif maximum** : Saisir le nombre max d'élèves
5. **Salle** : Sélectionner la salle assignée (optionnel)
6. Cliquer sur **[Enregistrer]**

### 4.2 Créer une matière
**Pourquoi** : Les matières définissent les enseignements dispensés.

**Cheminement** : **Enseignement** → **Matières** → **[Ajouter une matière]**

**Étapes** :
1. **Nom** : Saisir le nom (ex: `Mathématiques`)
2. **Code** : Saisir un code (ex: `MATH`)
3. **Coefficient** : Saisir le coefficient pour le calcul des moyennes
4. Cliquer sur **[Enregistrer]**

### 4.3 Créer un profil professeur
**Pourquoi** : Chaque professeur doit être lié à un compte utilisateur.

**Cheminement** : **Enseignement** → **Profils Professeurs** → **[Ajouter]**

**Étapes** :
1. **Utilisateur** : Sélectionner le compte utilisateur du professeur
2. **Spécialité** : Sélectionner la matière principale
3. **Grade** : Saisir le grade (optionnel)
4. Cliquer sur **[Enregistrer]**

### 4.4 Créer une attribution
**Pourquoi** : Pour assigner un professeur à une matière dans une classe.

**Cheminement** : **Enseignement** → **Attributions** → **[Ajouter]**

**Étapes** :
1. **Professeur** : Sélectionner le profil professeur
2. **Matière** : Sélectionner la matière
3. **Classe** : Sélectionner la classe
4. **Année scolaire** : Sélectionner l'année
5. Cliquer sur **[Enregistrer]**

### 4.5 Créer une salle
**Pourquoi** : Pour inventorier les salles disponibles.

**Cheminement** : **Enseignement** → **Salles** → **[Ajouter]**

**Étapes** :
1. **Nom** : Saisir le nom (ex: `Salle 101`)
2. **Capacité** : Nombre de places
3. **Type** : Sélectionner (Classe, Laboratoire, Sport, etc.)
4. **Bâtiment** : Saisir le bâtiment (optionnel)
5. Cliquer sur **[Enregistrer]**

---

## 5. GESTION DES ÉLÈVES

### 5.1 Enregistrer un élève
**Pourquoi** : Pour créer le dossier scolaire de l'élève.

**Cheminement** : **Scolarité** → **Élèves** → **[Ajouter un élève]**

**Étapes** :
Onglet Informations générales :
1. **Nom** : Saisir le nom de famille
2. **Prénom** : Saisir le prénom
3. **Sexe** : Sélectionner Masculin/Féminin
4. **Date de naissance** : Sélectionner la date
5. **Lieu de naissance** : Saisir la ville
6. **Adresse** : Saisir l'adresse complète

Onglet Informations familiales :
1. **Numéro matricule** : Auto-généré (peut être modifié)
2. **Date d'inscription** : Date du jour

3. Cliquer sur **[Enregistrer]**

**Vérifier** : Le matricule est généré automatiquement au format `ELV-ANNÉE-NUMÉRO`

### 5.2 Ajouter un parent/tuteur
**Pourquoi** : Pour enregistrer les responsables légaux.

**Étapes** :
1. Dans la fiche élève, aller dans l'onglet **Parents/Tuteurs**
2. Cliquer sur **[Ajouter un parent]**
3. Remplir les coordonnées (Nom, Prénom, Téléphone, Email, Lien de parenté)
4. Cliquer sur **[Enregistrer]**

### 5.3 Ajouter un dossier médical
**Pourquoi** : Pour consigner les informations médicales importantes.

**Étapes** :
1. Dans la fiche élève, aller dans **Dossier médical**
2. Remplir : Groupe sanguin, Allergies, Maladies chroniques, Contacts d'urgence
3. Cliquer sur **[Enregistrer]**

### 5.4 Inscrire un élève dans une classe
**Pourquoi** : Un élève doit être inscrit pour assister aux cours.

**Cheminement** : **Scolarité** → **Inscriptions** → **[Ajouter]**

**Étapes** :
1. **Élève** : Sélectionner l'élève
2. **Classe** : Sélectionner la classe
3. **Année scolaire** : Sélectionner l'année
4. **Date d'inscription** : Date de début
5. **Statut** : Sélectionner `Actif`
6. Cliquer sur **[Enregistrer]**

### 5.5 Enregistrer une sanction/récompense
**Pourquoi** : Pour tracer le comportement de l'élève.

**Cheminement** : **Scolarité** → **Sanctions & Récompenses** → **[Ajouter]**

**Étapes** :
1. **Élève** : Sélectionner l'élève
2. **Type** : Sélectionner Sanction ou Récompense
3. **Motif** : Décrire le motif
4. **Date** : Date de l'événement
5. **Gravité** : Sélectionner le niveau
6. **Description** : Détails supplémentaires
7. Cliquer sur **[Enregistrer]**

---

## 6. SUIVI DES PRÉSENCES

### 6.1 Créer une séance de cours
**Pourquoi** : Pour démarrer une séance d'appel.

**Cheminement** : **Présences** → **Séances de cours** → **[Créer]**

**Étapes** :
1. **Professeur** : Cette valeur est automatiquement la votre
2. **Classe** : Sélectionner la classe
3. **Matière** : Sélectionner la matière
4. **Date** : Sélectionner la date du jour
5. **Heure de début** : Sélectionner l'heure
6. **Durée** : Nombre de minutes
7. Cliquer sur **[Démarrer la séance]** ou **[Enregistrer]**

### 6.2 Effectuer l'appel
**Pourquoi** : Pour enregistrer la présence des élèves.

**Étapes** :
1. Après le démarrage, la liste des élèves apparaît
2. Pour chaque élève, sélectionner l'état :
   - **Présent** : Cliquer sur le bouton vert
   - **Absent** : Cliquer sur le bouton rouge (une fenêtre demande le motif)
   - **Retard** : Cliquer sur le bouton orange (préciser les minutes de retard)
3. Cliquer sur **[Valider l'appel]**

**Vérifier** :
- Un message confirme l'enregistrement
- Les statistiques se mettent à jour

### 6.3 Consulter les statistiques
**Cheminement** : **Présences** → **Statistiques**

**Options** :
- Filtrer par classe
- Filtrer par période (date début / fin)
- Exporter en PDF ou Excel

---

## 7. ÉVALUATIONS ET NOTES

### 7.1 Créer un examen
**Pourquoi** : Pour planifier une évaluation.

**Cheminement** : **Enseignement** → **Examens** → **[Créer]**

**Étapes** :
1. **Titre** : Saisir le nom (ex: `Devoir surveillé n°1`)
2. **Classe** : Sélectionner la classe
3. **Matière** : Sélectionner la matière
4. **Période** : Sélectionner le trimestre
5. **Date** : Sélectionner la date
6. **Coefficient** : Saisir le coefficient
7. **Durée** : Durée en minutes
8. Cliquer sur **[Enregistrer]**

### 7.2 Saisir les notes
**Pourquoi** : Pour enregistrer les notes des élèves.

**Étapes** :
1. Dans la liste des examens, cliquer sur l'examen créé
2. Une **grille de saisie** s'affiche
3. Dans le champ à côté de chaque élève, saisir la **note sur 20**
4. Cliquer sur **[Enregistrer les notes]**

### 7.3 Consulter les fiches de notes
**Pourquoi** : Pour voir les moyennes par élève.

**Cheminement** : **Enseignement** → **Fiches de notes**

**Étapes** :
1. Sélectionner la **Classe**
2. Sélectionner la **Matière**
3. Sélectionner la **Période**
4. Cliquer sur **[Générer]**
5. Voir le tableau avec :
   - Notes de chaque évaluation
   - Moyenne par matière
   - Rang de l'élève

### 7.4 Clôturer une période
**Pourquoi** : Pour verrouiller les notes et empêcher toute modification.

**Cheminement** : **Scolarité** → **Clôture des périodes**

**Étapes** :
1. Sélectionner la **Période** à clôture
2. Vérifier que toutes les notes sont saisies
3. Cliquer sur **[Clôturer la période]**
4. Confirmer la clôture

**Attention** : Après clôture, les notes ne peuvent plus être modifiées.

---

## 8. FINANCES ET COMPTABILITÉ

### 8.1 Définir les frais scolaires
**Pourquoi** : Pour fixer le montant à payer par élève.

**Cheminement** : **Finances** → **Frais scolaires** → **[Ajouter]**

**Étapes** :
1. **Libellé** : Nom des frais (ex: `Frais de scolarité 2025-2026`)
2. **Montant** : Montant en francs CFA
3. **Classe** : Sélectionner la classe (ou laisser vide pour tous)
4. **Année scolaire** : Sélectionner l'année
5. **Date d'échéance** : Date limite de paiement
6. **Description** : Détails supplémentaires
7. Cliquer sur **[Enregistrer]**

### 8.2 Enregistrer un paiement
**Pourquoi** : Pour enregistrer l'argent reçu.

**Cheminement** : **Finances** → **Paiements** → **[Ajouter]**

**Étapes** :
1. **Élève** : Sélectionner l'élève
2. **Montant** : Montant payé
3. **Date du paiement** : Date du jour
4. **Mode de paiement** : Espèces, Chèque, Virement bancaire
5. **Référence** : Numéro de reçu (auto-généré)
6. **Observations** : Notes éventuelles
7. Cliquer sur **[Enregistrer]**

**Vérifier** :
- Le reçu se génère automatiquement
- Le montant apparaît dans la fiche élève
- La dette restante se met à jour

### 8.3 Gérer la caisse
**Pourquoi** : Pour suivre les entrées et sorties d'argent.

**Cheminement** : **Finances** → **Caisse**

**Pour ouvrir la caisse** :
1. Cliquer sur **[Ouvrir la caisse]**
2. Saisir le montant initial
3. Valider

**Pour enregistrer une opération** :
1. Cliquer sur **[Nouvelle opération]**
2. **Type** : Encaissement (entrée) ou Dépense (sortie)
3. **Montant** : Somme
4. **Description** : Motif
5. **Date** : Date de l'opération
6. Cliquer sur **[Enregistrer]**

**Vérifier** : Le solde se met à jour automatiquement

### 8.4 Créer une facture
**Pourquoi** : Pour générer un document officiel pour les parents.

**Cheminement** : **Finances** → **Factures** → **[Générer]**

**Étapes** :
1. Sélectionner l'élève
2. Sélectionner l'année scolaire
3. Cliquer sur **[Générer la facture]**
4. Le PDF se télécharge

### 8.5 Gérer les charges
**Pourquoi** : Pour enregistrer les dépenses récurrentes.

**Cheminement** : **Finances** → **Charges** → **[Ajouter]**

**Types de charges** :
- **Charges fixes** : Loyer, eau, électricité
- **Charges opérationnelles** : Fournitures, réparation

---

## 9. RESSOURCES HUMAINES

### 9.1 Créer un membre du personnel
**Pourquoi** : Pour gérer tout le personnel de l'établissement.

**Cheminement** : **Ressources Humaines** → **Personnel** → **[Ajouter]**

**Étapes** :
1. **Nom** : Nom de famille
2. **Prénom** : Prénom
3. **Fonction** : Poste occupé
4. **Date d'embauche** : Date de début
5. **Salaire de base** : Montant mensuel
6. **Type de contrat** : CDI, CDD, Vacataire
7. Cliquer sur **[Enregistrer]**

### 9.2 Enregistrer un salaire
**Pourquoi** : Pour générer les bulletins de paie.

**Cheminement** : **Ressources Humaines** → **Salaires** → **[Ajouter]**

**Étapes** :
1. **Membre du personnel** : Sélectionner le membre
2. **Mois** : Mois concerné
3. **Salaire brut** : Montant brut
4. **Salaire net** : Montant après retenue
5. **Date de paiement** : Date de verseme
6. **Mode de paiement** : Espèces, Virement
7. Cliquer sur **[Enregistrer]**

### 9.3 Gérer les congés
**Cheminement** : **Ressources Humaines** → **Congés**

**Types** :
- Congé annuel
- Congé maladie
- Congé sans solde

---

## 10. RAPPORTS ET BULLETINS

### 10.1 Générer un bulletin individuel
**Pourquoi** : Pour remettre le document aux parents.

**Cheminement** : **Rapports** → **Bulletins** → **[Générer]**

**Étapes** :
1. **Élève** : Sélectionner l'élève
2. **Classe** : Sélectionner la classe
3. **Période** : Sélectionner le trimestre
4. Cliquer sur **[Générer le bulletin]**
5. Le fichier PDF se télécharge

### 10.2 Générer un rapport de classe
**Pourquoi** : Pour avoir une vue d'ensemble.

**Étapes** :
1. Sélectionner la **Classe**
2. Sélectionner la **Période**
3. Cliquer sur **[Générer]**

### 10.3 Générer un rapport financier
**Cheminement** : **Rapports** → **Rapport financier**

**Étapes** :
1. Sélectionner la **Période**
2. Cliquer sur **[Générer]**
3. Voir le résumé des :
   - Total des encaissements
   - Total des dépenses
   - Solde de la période

---

## 11. COMMUNICATION INTERNE

### 11.1 Envoyer une notification
**Pourquoi** : Pour alerter les utilisateurs.

**Cheminement** : **Authentification** → **Notifications** → **[Nouvelle notification]**

**Étapes** :
1. **Titre** : Sujet de la notification
2. **Destinataires** : Sélectionner un ou plusieurs utilisateurs
3. **Message** : Contenu du message
4. Sélectionner le **Type** : Info, Avertissement, Important
5. Cliquer sur **[Envoyer]**

### 11.2 Consulter mes notifications
**Cheminement** : Cliquer sur l'icône **cloche** dans la barre supérieure

### 11.3 Envoyer un message interne
**Pourquoi** : Pour communiquer entre membres du personnel.

**Cheminement** : **Authentification** → **Messages** → **[Nouveau message]**

---

## 12. RÔLES ET PERMISSIONS

### 12.1 Vue d'ensemble des rôles

Le système gère les accès par **rôles prédéfinis**. Chaque utilisateur se voit assigner un rôle qui détermine les modules auxquels il peut accéder.

**Rôles disponibles** :
- **Direction** : Gestion complète de l'établissement
- **Secrétaire** : Gestion des élèves et inscriptions
- **Comptable** : Gestion financière et comptable
- **Professeur** : Enseignement, notes et présences
- **Surveillance** : Contrôle des présences et discipline

> **Note** : Le rôle **Super Administrateur** existe pour la configuration technique du système mais n'est pas destiné à l'utilisation quotidienne.

### 12.2 Récapitulatif des accès par rôle

| Rôle | Modules Principaux | Permissions |
|------|-------------------|-------------|
| **Direction** | Tous les modules | CRUD complet sur tous les modules de gestion |
| **Secrétaire** | Scolarité, Enseignement (Lecture), Rapports | Gestion complète des élèves, inscriptions, discipline |
| **Comptable** | Finances, Scolarité (Lecture), Rapports | Gestion complète des paiements, caisse, charges, salaires |
| **Professeur** | Espace Enseignant, Présences, Notes | Saisie des notes, appel, gestion de ses classes |
| **Surveillance** | Présences, Discipline, Élèves (Lecture) | Appel pour toutes les classes, gestion des sanctions |

### 12.3 Détail des permissions par rôle

#### Direction
**Accès** : Tous les modules
**Responsabilités** :
- Configuration de l'année scolaire
- Création des classes et matières
- Gestion des utilisateurs
- Validation des bulletins et rapports
- Supervision de tous les services

#### Secrétaire
**Accès** :
- **Scolarité** : Élèves (CRUD), Inscriptions (CRUD), Discipline (CRUD), Dossiers médicaux, Documents
- **Enseignement** : Classes, Professeurs, Matières (Lecture seule)
- **Rapports** : Bulletins, Fiches de notes (Lecture/Export)
- **Configuration** : Années scolaires (Lecture)

**Responsabilités** :
- Enregistrement des nouveaux élèves
- Gestion des inscriptions
- Suivi des dossiers médicaux
- Tenue à jour des documents des élèves

#### Comptable
**Accès** :
- **Finances** : Frais scolaires, Paiements, Caisse, Charges, Factures, Bourses (CRUD)
- **Ressources Humaines** : Salaires (CRUD), Personnel (Lecture)
- **Scolarité** : Élèves, Inscriptions (Lecture seule)
- **Rapports** : Rapport financier, Statistiques globales

**Responsabilités** :
- Enregistrement des paiements
- Suivi de la caisse
- Gestion des frais scolaires
- Émission des factures
- Paiement des salaires
- Rapports financiers

#### Professeur
**Accès** :
- **Espace Enseignant** : Mes classes, Mes séances, Saisie des notes, Emploi du temps
- **Enseignement** : Matières, Attributions (Lecture)
- **Présences** : Mes séances de cours
- **Communication** : Notifications, Messages

**Responsabilités** :
- Préparation et déroulement des cours
- Saisie des notes d'évaluation
- Suivi des présences dans ses classes
- Communication avec la direction et les parents

#### Surveillance
**Accès** :
- **Présences** : Appel, Statistiques, Rapport des retards (CRUD)
- **Scolarité** : Discipline (CRUD), Élèves (Lecture)
- **Communication** : Notifications, Messages (Lecture)

**Responsabilités** :
- Contrôle des présences dans toutes les classes
- Gestion des retards et absences
- Application du règlement intérieur
- Gestion des sanctions et récompenses

### 12.4 Gestion des permissions
**Cheminement** : **Administration** → **Gestion des permissions**

**Fonctionnalités** :
- Activer/Désactiver des modules pour un rôle spécifique
- Créer des **permissions personnalisées** par utilisateur
- Consulter l'historique des accès

**Important** : Les permissions par défaut sont configurées via la commande :
```bash
python manage.py init_modules
```

### 12.5 Bonnes pratiques de sécurité

1. **Ne partagez pas vos identifiants** : Chaque utilisateur doit avoir son propre compte
2. **Déconnectez-vous** : Toujours se déconnecter en quittant le poste de travail
3. **Mot de passe robuste** : Utiliser des mots de passe complexes (min. 8 caractères, majuscules, minuscules, chiffres)
4. **Rôle approprié** : Assigner le rôle minimum nécessaire à chaque utilisateur
5. **Révision régulière** : Vérifier périodiquement les accès et désactiver les comptes inactifs

---

## 13. DÉPANNAGE

### 13.1 Problèmes courants

**Je ne peux pas me connecter**
- Vérifier que le compte est **approuvé** et **actif**
- Vérifier le mot de passe

**Je ne vois pas mes élèves dans l'appel**
- Vérifier qu'ils sont **inscrits** dans la classe
- Vérifier l'année scolaire

**Les notes ne s'enregistrent pas**
- Vérifier que la période n'est pas **clôturée**

**Le bulletin ne se génère pas**
- Vérifier que toutes les notes sont saisies
- Vérifier que l'élève est inscrit

### 13.2 Contacter le support
En cas de problème non résolu, contacter l'administrateur système.

---

*Dernière mise à jour : 19 Avril 2026*
*Version : 2.1 - SyGeS-AM*

## Documents associés

- **[Guide de Test Complet](GUIDE_TEST_COMPLET.md)** : Guide de test détaillé (vue Super Admin)
- **[Guide de Test par Rôles](GUIDE_TEST_PAR_ROLES.md)** : Guide de test chronologique par rôles utilisateurs