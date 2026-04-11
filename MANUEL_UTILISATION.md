# Manuel d'Utilisation - Système de Gestion Scolaire SyGeS-AM

## Table des Matières

1. [Introduction](#1-introduction)
2. [Rôles et Permissions](#2-rôles-et-permissions)
3. [Phase 1 : Configuration Initiale](#3-phase-1--configuration-initiale)
4. [Phase 2 : Inscription des Élèves](#4-phase-2--inscription-des-élèves)
5. [Phase 3 : Gestion du Personnel](#5-phase-3--gestion-du-personnel)
6. [Phase 4 : Organisation Académique](#6-phase-4--organisation-académique)
7. [Phase 5 : Emploi du Temps](#7-phase-5--emploi-du-temps)
8. [Phase 6 : Examens et Évaluations](#8-phase-6--examens-et-évaluations)
9. [Phase 7 : Bulletins et Rapports](#9-phase-7--bulletins-et-rapports)
10. [Phase 8 : Présences et Séances](#10-phase-8--présences-et-séances)
11. [Phase 9 : Finances](#11-phase-9--finances)
12. [Phase 10 : Communication](#12-phase-10--communication)
13. [Phase 11 : Administration](#13-phase-11--administration)
14. [Flux de Travail Récapitulatifs](#14-flux-de-travail-récapitulatifs)
15. [Dépannage](#15-dépannage)
16. [API REST](#16-api-rest)
17. [Export de Données](#17-export-de-données)
18. [Notifications par Email](#18-notifications-par-email)
19. [Sauvegardes](#19-sauvegardes)
20. [Ressources Humaines - Congés et Absences](#20-ressources-humaines---congés-et-absences)
21. [Tableau de Bord Avancé](#21-tableau-de-bord-avancé)
22. [Sécurités et Bonnes Pratiques](#22-sécurités-et-bonnes-pratiques)

---

## 1. Introduction

### 1.1 Accès au Système
- **URL locale** : `http://127.0.0.1:8000/`
- **URL production** : `https://votre-domaine.com/`
- **Navigateurs compatibles** : Chrome, Firefox, Edge (versions récentes)

### 1.2 Processus de Connexion
1. Saisir le nom d'utilisateur et mot de passe
2. Cliquer sur "Se connecter"
3. Si 2FA activé, saisir le code du приложения d'authentification
4. Le tableau de bord s'affiche selon le rôle

### 1.3 Sécurité - Authentification à Deux Facteurs (2FA)
**Activation (Utilisateur) :**
1. Aller dans **Profil**
2. Cliquer sur "Activer 2FA"
3. Scanner le code QR avec Google Authenticator
4. Saisir le code pour confirmer
5. **Important** : Sauvegarder les codes de secours

### 1.4 Tableau de Bord
- Vue d'ensemble selon le rôle
- Notifications importantes
- Accès rapides aux tâches quotidiennes

---

## 2. Rôles et Permissions

### 2.1 Description des Rôles

| Rôle | Description | Permissions Principales |
|------|-------------|-------------------------|
| **Super Administrateur** | Administrateur système | Accès total, Django Admin, configuration |
| **Direction** | Responsable établissement | Gestion complète sauf Admin Django |
| **Secrétaire** | Gestion quotidienne | Scolarité, classes, présence, secrétariat |
| **Comptable** | Gestion financière | Finances, salaires, paiements |
| **Professeur** | Enseignant | Ses classes, notes, présences |
| **Surveillance** | Contrôle | Présences, suivi, ponctualité |

### 2.2 Architecture des Services
Le système est organisé en 10 services principaux :

| # | Service | Description | Modules clés |
|---|---------|-------------|--------------|
| 1 | **Scolarité** | Gestion des élèves | Élèves, Inscriptions, Discipline, Documents |
| 2 | **Enseignement** | Organisation académique | Classes, Matières, Professeurs, Examens |
| 3 | **Espace Enseignant** | Interface professeur | Mes Classes, Emploi du temps, Saisie notes |
| 4 | **Présences** | Suivi des présences | Appel, Statistiques, Rapports retards |
| 5 | **Communication** | Notifications et messages | Notifications, Messages |
| 6 | **Finances** | Gestion financière | Frais, Paiements, Caisse, Charges |
| 7 | **Ressources Humaines** | Personnel | Personnel, Salaires, Postes, Contrats |
| 8 | **Rapports** | Bulletins et statistiques | Bulletins, Fiches de notes, Rapports |
| 9 | **Configuration** | Paramétrage | Années scolaires, Salles |
| 10 | **Administration** | Gestion système | Utilisateurs, Permissions, Approbations |

### 2.2 Tableau des Accès par Module

| Module | Super Admin | Direction | Secrétaire | Comptable | Professeur | Surveillance |
|--------|:-----------:|:---------:|:----------:|:---------:|:----------:|:------------:|
| **Gestion des élèves** | | | | | | |
| Élèves | ✓ | ✓ | ✓ | - | - | - |
| Dossiers médicaux | ✓ | ✓ | ✓ | - | - | - |
| Documents | ✓ | ✓ | ✓ | - | - | - |
| Discipline | ✓ | ✓ | ✓ | - | - | - |
| Parents/Tuteurs | ✓ | ✓ | ✓ | - | - | - |
| **Gestion académique** | | | | | | |
| Classes | ✓ | ✓ | ✓ | - | - | - |
| Professeurs | ✓ | ✓ | ✓ | - | - | - |
| Matières | ✓ | ✓ | ✓ | - | - | - |
| Salles | ✓ | ✓ | ✓ | - | - | - |
| Attributions | ✓ | ✓ | ✓ | - | - | - |
| Coefficients | ✓ | ✓ | ✓ | - | - | - |
| Contraintes horaires | ✓ | ✓ | ✓ | - | - | - |
| Examens | ✓ | ✓ | ✓ | - | - | - |
| **Notes & Bulletins** | | | | | | |
| Saisie notes | ✓ | ✓ | ✓ | - | ✓ | - |
| Fiches de notes | ✓ | ✓ | ✓ | - | - | - |
| Bulletins | ✓ | ✓ | ✓ | - | - | - |
| Rapports académiques | ✓ | ✓ | ✓ | - | - | - |
| **Espace Professeur** | | | | | | |
| Mes Classes | ✓ | - | - | - | ✓ | - |
| Mon Emploi du temps | ✓ | - | - | - | ✓ | - |
| Mes Séances | ✓ | - | - | - | ✓ | - |
| **Présences** | | | | | | |
| Présences | ✓ | ✓ | ✓ | - | ✓ | ✓ |
| Statistiques | ✓ | ✓ | - | - | - | ✓ |
| Rapports Retards | ✓ | ✓ | - | - | - | ✓ |
| Attestations | ✓ | ✓ | - | - | - | ✓ |
| Séances Cours | ✓ | ✓ | - | - | ✓ | ✓ |
| **Finances** | | | | | | |
| Frais scolaires | ✓ | ✓ | - | ✓ | - | - |
| Factures | ✓ | ✓ | - | ✓ | - | - |
| Bourses & Remises | ✓ | ✓ | - | ✓ | - | - |
| Paiements | ✓ | ✓ | - | ✓ | - | - |
| Relances | ✓ | ✓ | - | ✓ | - | - |
| Rapports financiers | ✓ | ✓ | - | ✓ | - | - |
| Catégories dépenses | ✓ | ✓ | - | ✓ | - | - |
| **Personnel** | | | | | | |
| Personnel | ✓ | ✓ | - | ✓ | - | - |
| Opérations caisse | ✓ | ✓ | - | ✓ | - | - |
| Charges école | ✓ | ✓ | - | ✓ | - | - |
| Salaires | ✓ | ✓ | - | ✓ | - | - |
| **Administration** | | | | | | |
| Années scolaires | ✓ | ✓ | - | - | - | - |
| Utilisateurs | ✓ | ✓ | - | - | - | - |
| Approbations | ✓ | ✓ | ✓ | - | - | - |
| Rapports | ✓ | ✓ | ✓ | - | - | - |
| Admin Django | ✓ | - | - | - | - | - |
| **Communication** | | | | | | |
| Notifications | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Messages | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## 3. Phase 1 : Configuration Initiale

### 3.1 Création de l'Année Scolaire
**Chemin** : `Administration` → `Années scolaires`
**Accès** : Direction, Super Admin
**Moment** : Avant chaque début d'année scolaire

**Procédure :**
1. Cliquer `Créer une année scolaire`
2. Remplir :
   - Libellé (ex: 2025-2026)
   - Date de début
   - Date de fin
   - Cocher "Année active" (une seule active à la fois)
3. Valider

**Astuce** : Une seule année peut être active à la fois. Pour changer d'année, désactiver l'ancienne et activer la nouvelle.

### 3.2 Configuration des Cycles de Paiement
**Chemin** : `Finances` → `Cycles de paiement`
**Accès** : Direction, Comptable
**Moment** : Lors de la configuration initiale des finances

**Procédure :**
1. Cliquer `Ajouter un cycle`
2. Remplir :
   - Nom (ex: Trimestre 1)
   - Dates de début et fin
   - Pourcentage des frais à payer

**Types de cycles** :
- Trimestriel (3 cycles)
- Semestriel (2 cycles)

### 3.3 Définition des Frais Scolaires
**Chemin** : `Finances` → `Frais scolaires`
**Accès** : Direction, Comptable
**Moment** : Chaque année scolaire

**Procédure :**
1. Cliquer `Ajouter des frais`
2. Remplir :
   - Classe concernée
   - Type de frais (Minerval, Scolarité, Prière, etc.)
   - Montant
   - Cycle de paiement applicable
3. Valider

---

## 4. Phase 2 : Inscription des Élèves

### 4.1 Enregistrement d'un Nouvel Élève
**Chemin** : `Gestion des élèves` → `Élèves`
**Accès** : Direction, Secrétaire
**Moment** : Période d'inscription

**Procédure :**
1. Cliquer `Nouvel élève`
2. Remplir les informations :
   - Nom, Prénom
   - Date de naissance
   - Sexe
   - Adresse complète
   - Nom du père
   - Nom de la mère
   - Téléphone parent
3. Valider

### 4.2 Inscription en Classe
**Chemin** : `Gestion des élèves` → `Élèves` → `[Élève]` → `Modifier`
**Accès** : Direction, Secrétaire

**Procédure :**
1. Sélectionner l'élève
2. Choisir la classe
3. Sélectionner l'année scolaire active
4. Valider

### 4.3 Gestion des Dossiers Médicaux
**Chemin** : `Gestion des élèves` → `Dossiers médicaux`
**Accès** : Direction, Secrétaire
**Moment** : Obligatoire lors de l'inscription, mise à jour annuelle

**Contenu** :
- Allergies (alimentaires, médicamenteuses, etc.)
- Traitements en cours
- Contacts d'urgence
- Restrictions alimentaires
- Particularités de santé

**Procédure :**
1. Sélectionner l'élève
2. Remplir les informations médicales
3. Ajouter les contacts d'urgence
4. Valider

### 4.4 Upload des Documents
**Chemin** : `Gestion des élèves` → `Documents`
**Accès** : Direction, Secrétaire
**Moment** : Lors de l'inscription

**Documents requis** :
- Acte de naissance (obligatoire)
- Photos d'identité
- Certificat de scolarité (pour transfert)
- Certificat médical
- Documents des parents/tuteurs

**Procédure :**
1. Sélectionner l'élève
2. Cliquer `Ajouter un document`
3. Sélectionner le type de document
4. Upload le fichier
5. Valider

### 4.5 Gestion des Parents/Tuteurs
**Chemin** : `Gestion des élèves` → `Parents/Tuteurs`
**Accès** : Direction, Secrétaire

**Information stockée** :
- Nom complet
- Lien avec l'élève
- Téléphone (avec indication WhatsApp)
- Email
- Adresse

**Procédure :**
1. Cliquer `Nouveau parent`
2. Remplir les informations
3. Associer les enfants
4. Valider

---

## 5. Phase 3 : Gestion du Personnel

### 5.1 Ajout d'un Professeur
**Chemin** : `Gestion académique` → `Professeurs`
**Accès** : Direction, Secrétaire
**Moment** : Lors du recrutement

**Procédure :**
1. Cliquer `Nouveau professeur`
2. Remplir :
   - Nom, Prénom
   - Email
   - Téléphone
   - Date d'embauche
   - Salaire de base
3. Valider

### 5.2 Création du Compte Utilisateur
**Chemin** : `Administration` → `Utilisateurs`
**Accès** : Direction, Super Admin

**Procédure :**
1. Cliquer `Nouvel utilisateur`
2. Remplir :
   - Nom d'utilisateur
   - Rôle : "Enseignement"
   - Email, Prénom, Nom
   - Fonction : Professeur
3. Valider
4. **Approuver** le compte (`Utilisateurs` → `Approuver`)

### 5.3 Ajout du Personnel Administratif
**Chemin** : `Gestion du personnel` → `Personnel`
**Accès** : Direction, Comptable

**Types de personnel** :
- Secrétaire
- Comptable
- Agent de surveillance
- Agent d'entretien
- Gardien

**Procédure :**
1. Cliquer `Nouveau personnel`
2. Remplir les informations
3. Définir le poste
4. Valider

### 5.4 Création Compte Personnel
**Chemin** : `Administration` → `Utilisateurs`
**Accès** : Direction, Super Admin

**Rôles disponibles** :
- Comptabilité
- Secrétariat
- Surveillance
- Agent

---

## 6. Phase 4 : Organisation Académique

### 6.1 Création des Classes
**Chemin** : `Gestion académique` → `Classes`
**Accès** : Direction, Secrétaire
**Moment** : Avant la rentrée ou en cours d'année

**Procédure :**
1. Cliquer `Nouvelle classe`
2. Remplir :
   - Nom de la classe
   - Niveau (6e, 5e, 4e, 3e, 2nde, 1re, Tle)
   - Capacité maximale
   - Filière (pour le lycée : Scientifique, Littéraire, etc.)
3. Valider

### 6.2 Création des Salles
**Chemin** : `Gestion académique` → `Salles`
**Accès** : Direction, Secrétaire
**Moment** : Configuration initiale

**Types de salles** :
- Salle de classe
- Laboratoire
- Salle informatique
- Salle de sport
- Bibliothèque
- Autre

**Procédure :**
1. Cliquer `Nouvelle salle`
2. Remplir :
   - Nom
   - Type
   - Capacité
   - Étage
   - Équipements (vidéoprojecteur, tableau interactif, etc.)
3. Valider

### 6.3 Ajout des Matières
**Chemin** : `Gestion académique` → `Matières`
**Accès** : Direction, Secrétaire

**Procédure :**
1. Cliquer `Nouvelle matière`
2. Remplir :
   - Nom de la matière
   - Classe (optionnel : toutes classes ou une spécifique)
   - Coefficient par défaut
3. Valider

**Note** : Si la matière est spécifique à une classe, sélectionner cette classe.

### 6.4 Attribution des Matières aux Professeurs
**Chemin** : `Gestion académique` → `Attributions`
**Accès** : Direction, Secrétaire
**Moment** : Après la création des classes et matières

**Procédure :**
1. Cliquer `Nouvelle attribution`
2. Sélectionner :
   - Classe
   - Matière
   - Professeur
   - Année scolaire
3. Valider

### 6.5 Définition des Coefficients
**Chemin** : `Gestion académique` → `Coefficients`
**Accès** : Direction, Secrétaire
**Moment** : Après création des classes et matières

**Procédure :**
1. Cliquer `Nouveau coefficient`
2. Sélectionner :
   - Classe
   - Matière
3. Définir le coefficient (1, 2, 3, etc.)
4. Valider

**Importance** : Les coefficients influencent le calcul des moyennes générales.

### 6.6 Gestion de la Discipline
**Chemin** : `Gestion des élèves` → `Discipline`
**Accès** : Direction, Secrétaire
**Moment** : À chaque incident

**Types d'actions** :
- **Sanctions** : Avertissement oral, avertissement écrit, retenue, exclusion temporaire
- **Récompenses** : Félicitations, mention bien, prix d'excellence

**Procédure :**
1. Sélectionner l'élève
2. Cliquer `Nouvelle action`
3. Choisir le type (sanction/récompense)
4. Décrire l'incident ou la raison
5. Définir la sanction ou récompense
6. Valider

---

## 7. Phase 5 : Emploi du Temps

### 7.1 Définition des Contraintes Horaires
**Chemin** : `Gestion académique` → `Contraintes horaires`
**Accès** : Direction, Secrétaire
**Moment** : Avant la création de l'emploi du temps

**Types de contraintes** :
- Indisponible (congé, maladie)
- Préférence (horaire souhaité)
- Cours d'EPS (terrain extérieur)
- Réunion
- Autre

**Procédure :**
1. Cliquer `Nouvelle contrainte`
2. Sélectionner le professeur
3. Définir :
   - Jour
   - Heure de début et fin
   - Type de contrainte
   - Motif
4. Cocher `Récurrent` si hebdomadaire
5. Valider

### 7.2 Création de l'Emploi du Temps
**Chemin** : `Gestion académique` → `Emploi du temps`
**Accès** : Direction, Secrétaire
**Moment** : Après les attributions

**Procédure :**
1. Sélectionner une attribution
2. Cliquer sur le créneau horaire souhaité
3. Définir le jour et les heures
4. Valider

**Gestion des conflits** :
- Le système signale si un professeur a déjà un cours à cet horaire
- Possibilité d'annuler et reprogrammer

### 7.3 Réinitialisation de l'Emploi du Temps
**Chemin** : `Gestion académique` → `Emploi du temps` → `Réinitialiser`
**Accès** : Direction, Super Admin

**Utilité** : Permet de repartir de zéro en cas de changement majeur.

### 7.4 Consultation par le Professeur
**Chemin** : `Espace enseignant` → `Emploi du temps`
**Accès** : Professeur

Le professeur voit son emploi du temps personnel basé sur ses attributions.

---

## 8. Phase 6 : Examens et Évaluations

### 8.1 Planification d'un Examen
**Chemin** : `Gestion académique` → `Examens`
**Accès** : Direction, Secrétaire
**Moment** : Selon le calendrier scolaire

**Types d'examens** :
- 1er Trimestre
- 2ème Trimestre
- 3ème Trimestre
- 1er Semestre
- 2ème Semestre
- Examen blanc
- Examen final
- Concours

**Procédure :**
1. Cliquer `Nouvel examen`
2. Remplir :
   - Nom de l'examen
   - Type (trimestre, semestre, etc.)
   - Classe
   - Matière
   - Date
   - Durée (en minutes)
   - Lieu (salle)
   - Surveillant
3. Valider

### 8.2 Génération des Épreuves
**Chemin** : `Gestion académique` → `Examens` → `[Examen]` → `Générer épreuves`
**Moment** : Après la création de l'examen

**Procédure :**
1. Ouvrir les détails de l'examen
2. Cliquer `Générer épreuves`
3. Le système crée automatiquement les copies pour tous les élèves de la classe

### 8.3 Correction et Saisie des Notes
**Chemin** : `Gestion académique` → `Examens` → `[Examen]` → `Détails`
**Accès** : Direction, Secrétaire

**Procédure :**
1. Ouvrir l'examen
2. Pour chaque élève :
   - Saisir la note
   - Ajouter une appréciation (optionnel)
3. Les copies passent en statut "Corrigé"

### 8.4 Publication des Résultats
**Chemin** : `Gestion académique` → `Examens` → `[Examen]` → `Publier résultats`
**Moment** : Après la correction

**Procédure :**
1. Vérifier que toutes les notes sont saisies
2. Cliquer `Publier résultats`
3. Les résultats deviennent visibles pour les élèves/parents

### 8.5 Saisie des Notes de Classe
**Chemin** : `Espace enseignant` → `Saisie Notes` (Professeur)
**Chemin** : `Gestion académique` → `Saisie Notes` (Direction/Secrétaire)

**Types d'évaluations** :
- Interrogation
- Mini Devoir
- Devoir
- Examen

**Procédure :**
1. Sélectionner la classe et la matière
2. Choisir le type d'évaluation
3. Saisir la date et le titre
4. Entrer les notes pour chaque élève
5. Valider

### 8.6 Consultation des Fiches de Notes
**Chemin** : `Gestion des élèves` → `Fiches de Notes`
**Accès** : Direction, Secrétaire

Permet de visualiser les moyennes par matière et par cycle pour chaque élève.

---

## 9. Phase 7 : Bulletins et Rapports

### 9.1 Génération des Bulletins
**Chemin** : `Gestion des élèves` → `Bulletins`
**Accès** : Direction, Secrétaire
**Moment** : Fin de chaque trimestre/semestre

**Procédure :**
1. Sélectionner la classe
2. Sélectionner le cycle (trimestre/semestre)
3. Cliquer `Générer les bulletins`
4. Le système calcule automatiquement :
   - Moyennes par matière
   - Moyenne générale
   - Rang dans la classe
   - Mention

### 9.2 Export PDF des Bulletins
**Chemin** : `Gestion des élèves` → `Bulletins` → `[Bulletin]` → `Exporter PDF`
**Accès** : Direction, Secrétaire

**Contenu du PDF** :
- En-tête de l'établissement
- Informations de l'élève
- Tableau des notes par matière
- Moyenne générale
- Rang et mention
- Appréciation générale
- Signature du Directeur

### 9.3 Rapport Académique
**Chemin** : `Administration` → `Rapports` → `Rapport Académique`
**Accès** : Direction, Secrétaire

**Contenu** :
- Statistiques par classe
- Moyennes générales
- Taux de réussite
- Meilleurs élèves

### 9.4 Transition vers Nouvelle Année
**Chemin** : `Administration` → `Rapports` → `Transition Année`
**Accès** : Direction, Super Admin
**Moment** : Fin d'année scolaire

**Actions** :
1. Clôturer l'année en cours
2. Générer automatiquement la nouvelle année
3. Promouvoir les élèves vers la classe supérieure
4. Archiver les données

---

## 10. Phase 8 : Présences et Séances

### 10.1 Enregistrement des Présences
**Chemin** : `Gestion des présences` → `Présences`
**Accès** : Tous les utilisateurs avec permissions

**Procédure :**
1. Sélectionner la classe
2. Pour chaque élève, marquer :
   - **P** : Présent
   - **A** : Absent
   - **R** : Retard
3. Ajouter des observations si nécessaire
4. Valider

### 10.2 Statistiques de Présence
**Chemin** : `Gestion des présences` → `Statistiques`
**Accès** : Direction, Surveillance

**Données disponibles** :
- Taux de présence par classe
- Nombre d'absences
- Nombre de retards
- Comparaison entre classes

### 10.3 Rapport des Retards
**Chemin** : `Gestion des présences` → `Rapports Retards`
**Accès** : Direction, Surveillance

**Utilité** :
- Identifier les élèves chroniquement en retard
- Préparer les sanctions pour ponctualité
- Convoquer les parents

### 10.4 Attestation d'Assiduité
**Chemin** : `Gestion des présences` → `Attestations`
**Accès** : Direction, Surveillance
**Moment** : Sur demande des parents

**Procédure :**
1. Rechercher l'élève (nom, prénom ou matricule)
2. Cliquer `Générer PDF`
3. Le document contient :
   - Informations de l'élève
   - Statistiques de présence
   - Taux d'assiduité
   - Signature du Directeur

### 10.5 Démarrage d'une Séance
**Chemin** : `Espace enseignant` → `Mes Séances`
**Accès** : Professeur

**Procédure :**
1. Sélectionner l'enseignement
2. Cliquer `Démarrer`
3. Le timer commence
4. **Notification** envoyée automatiquement à :
   - Direction
   - Surveillance

### 10.6 Clôture d'une Séance
**Chemin** : `Espace enseignant` → `Mes Séances` → `[Séance]` → `Terminer`
**Accès** : Professeur

**Procédure :**
1. Cliquer `Terminer la séance`
2. Ajouter des notes (optionnel)
3. Valider
4. La durée est enregistrée
5. **Notification** envoyée à Direction et Surveillance

### 10.7 Suivi des Séances
**Chemin** : `Gestion des présences` → `Séances Cours`
**Accès** : Direction, Surveillance

Permet de voir toutes les séances de la journée en cours.

---

## 11. Phase 9 : Finances

### 11.1 Enregistrement d'un Paiement
**Chemin** : `Finances` → `Paiements`
**Accès** : Direction, Comptable

**Modes de paiement** :
- Espèces
- Mobile Money
- Chèque
- Virement bancaire

**Procédure :**
1. Cliquer `Nouveau paiement`
2. Sélectionner l'élève
3. Remplir :
   - Montant versé
   - Mode de paiement
   - Date
   - Motif (scolarité, frais divers, etc.)
4. Valider → Reçu généré automatiquement

### 11.2 Génération de Factures
**Chemin** : `Finances` → `Factures`
**Accès** : Direction, Comptable

**Procédure :**
1. Cliquer `Nouvelle facture`
2. Sélectionner l'élève
3. Ajouter les lignes :
   - Description
   - Quantité
   - Prix unitaire
   - Remise (optionnel)
4. Valider
5. Cliquer `Télécharger PDF` pour obtenir la facture officielle

### 11.3 Gestion des Bourses et Remises
**Chemin** : `Finances` → `Bourses & Remises`
**Accès** : Direction, Comptable

**Types** :
- Bourse d'études (méritants)
- Remise familiale (frères/sœurs)
- Remise sociale (difficultés familiales)
- Exonération

**Procédure :**
1. Cliquer `Nouvelle bourse/remise`
2. Sélectionner le type
3. Définir le pourcentage
4. Sélectionner les élèves concernés
5. Valider

### 11.4 Gestion des Relances
**Chemin** : `Finances` → `Relances`
**Accès** : Direction, Comptable

**Procédure :**
1. Cliquer `Générer les rappels`
2. Le système identifie les élèves en retard
3. Consulter la liste
4. Envoyer des notifications

### 11.5 Consultation du Compte Élève
**Chemin** : `Finances` → `Paiements` → `État du compte` (icône)
**Accès** : Direction, Comptable

Affiche :
- Total des frais
- Montant payé
- Reste à payer
- Historique des paiements

### 11.6 Rapports Financiers
**Chemin** : `Finances` → `Rapports financiers`
**Accès** : Direction, Comptable

**Types de rapports** :
- Journalier
- Mensuel
- Trimestriel
- Annuel

**Procédure :**
1. Sélectionner la période
2. Cliquer `Générer`
3. Consulter :
   - Total encaissements
   - Total dépenses
   - Total salaires
   - Solde

### 11.7 Catégories de Dépenses
**Chemin** : `Finances` → `Catégories dépenses`
**Accès** : Direction, Comptable

**Utilité** : Classifier les dépenses pour les rapports analytiques.

### 11.8 Opérations de Caisse
**Chemin** : `Gestion du personnel` → `Opérations de caisse`
**Accès** : Direction, Comptable

**Types** :
- Encaissement (entrée d'argent)
- Décaissement (sortie d'argent)

**Procédure :**
1. Sélectionner le type
2. Saisir le montant
3. Ajouter une description
4. Valider

### 11.9 Gestion des Charges
**Chemin** : `Gestion du personnel` → `Charges de l'école`
**Accès** : Direction, Comptable

**Types de charges** :
- Charges fixes (loyer, abonnement, etc.)
- Charges opérationnelles (fournitures, entretiens, etc.)

### 11.10 Gestion des Salaires
**Chemin** : `Gestion du personnel` → `Personnel` → `[Personne]` → `Salaires`
**Accès** : Direction, Comptable

**Procédure :**
1. Sélectionner l'employé
2. Cliquer `Ajouter un salaire`
3. Remplir :
   - Mois et année
   - Salaire de base
   - Retenues (prêts, avances, etc.)
4. Valider

---

## 12. Phase 10 : Communication

### 12.1 Notifications
**Chemin** : Menu principal → `Notifications`
**Accès** : Tous les utilisateurs

**Types de notifications automatiques** :
- Début/fin de séances (Direction, Surveillance)
- Comptes à approuver (Direction)
- Paiements reçus (Comptable, Direction)
- Demandes d'approbation
- Alertes d'absence

**Actions** :
- Marquer comme lu
- Marquer tout comme lu
- Supprimer

### 12.2 Messages
**Chemin** : Menu principal → `Messages`
**Accès** : Tous les utilisateurs

**Fonctionnalités** :
- Conversations individuelles
- Messages de groupe
- Pièces jointes
- Historique

### 12.3 Système de Demandes d'Approbation
**Chemin** : `Administration` → `Approbations`
**Accès** : Direction, Secrétaire

**Utilisé pour** :
- Création de matières (avec approbation)
- Modification de matières
- Attribution de classes
- Suppressions importantes

**Actions** :
- Approuver
- Rejeter avec motif

---

## 13. Phase 11 : Administration

### 13.1 Gestion des Utilisateurs
**Chemin** : `Administration` → `Utilisateurs`
**Accès** : Direction, Super Admin

**Actions disponibles** :
- Créer un utilisateur
- Modifier les informations
- Changer le rôle
- Activer/Désactiver le compte
- Réinitialiser le mot de passe
- Approuver un nouveau compte

### 13.2 Réinitialisation de Mot de Passe
**Chemin** : `Administration` → `Utilisateurs` → `[Utilisateur]` → `Réinitialiser`
**Accès** : Direction, Super Admin

**Procédure :**
1. Cliquer sur l'icône clé
2. Saisir le nouveau mot de passe
3. Confirmer
4. Valider

### 13.3 Activation/Désactivation de Compte
**Chemin** : `Administration` → `Utilisateurs` → `[Utilisateur]` → `Activer/Désactiver`
**Accès** : Direction, Super Admin

Un compte désactivé ne peut plus se connecter.

### 13.4 Journal d'Audit
**Accès** : Super Admin (via Django Admin)

**Suivi** :
- Toutes les actions (création, modification, suppression)
- Par utilisateur
- Par date
- Par type d'action

---

## 14. Flux de Travail Récapitulatifs

### FLUX 1 : Inscription d'un Nouvel Élève
```
1. Secrétaire → Crée l'élève (Nom, prénom, date de naissance)
2. Secrétaire → Inscrit en classe (Année + Classe)
3. Secrétaire → Crée dossier médical (Santé, allergies, contacts urgence)
4. Secrétaire → Upload documents (Acte naissance, photos)
5. Secrétaire → Ajoute les parents/tuteurs (Coordonnées)
6. Direction → Valide si nécessaire
```

### FLUX 2 : Recrutement d'un Professeur
```
1. Direction → Crée le profil professeur (Infos personnelles)
2. Direction/Admin → Crée compte utilisateur + approuve
3. Comptable → Définit le salaire de base
4. Secrétaire → Lui attribue ses classes et matières
5. Secrétaire → Définit les contraintes horaires (si existant)
6. Professeur → Reçoit accès et se connecte
```

### FLUX 3 : Organisation d'un Examen
```
1. Direction/Secrétaire → Crée l'examen (Date, lieu, durée)
2. Direction/Secrétaire → Génère les épreuves (Copies pour tous)
3. Surveillant → Effectue la surveillance
4. Professeur/Secrétaire → Corrige et saisit les notes
5. Direction → Publie les résultats
6. Élèves/Parents → Consultent les résultats
```

### FLUX 4 : Paiement des Frais
```
1. Parent → Se présente à la comptabilité
2. Comptable → Vérifie le solde de l'élève
3. Comptable → Enregistre le paiement
4. Système → Génère le reçu automatiquement
5. Direction → Reçoit notification (si configuré)
6. Parent → Récupère le reçu
```

### FLUX 5 : Demande et Délivrance d'une Attestation
```
1. Parent → Fait la demande (téléphone, message, en personne)
2. Surveillance/Direction → Vérifie les présences
3. Direction → Génère l'attestation PDF
4. Parent → Récupère le document signé
```

### FLUX 6 : Démarrage et Fin d'un Cours
```
1. Professeur → Se connecte
2. Professeur → Démarre la séance
   ↓
   Direction + Surveillance → Notification de début
   ↓
3. Professeur → Fait l'appel (marque présences)
4. Professeur → Enseigne
5. Professeur → Termine la séance
   ↓
   Direction + Surveillance → Notification de fin + durée
   ↓
6. Système → Enregistre la durée effective
```

### FLUX 7 : Clôture de l'Année Scolaire
```
1. Direction → Génère le rapport annuel
2. Direction → Initie la clôture
   ↓
   Système → Génère automatiquement la nouvelle année
   ↓
3. Système → Propose la promotion des élèves
4. Direction → Valide les promotions
5. Système → Archive les données de l'année
6. Direction → Génère les attestations de fin d'année
```

---

## 15. Dépannage

### Problèmes Courants et Solutions

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| Impossible de se connecter | Compte non approuvé | Contacter la direction |
| Menu incomplet | Rôle non configuré | Vérifier le rôle dans Admin |
| Données d'élève manquantes | Mauvaise année sélectionnée | Changer l'année dans la barre |
| PDF non généré | Erreur ReportLab | Vérifier les logs serveur |
| Examens sans élèves | Classe non associée | Vérifier les inscriptions |
| Moyennes incorrectes | Coefficients non définis | Définir les coefficients |
| Paiement non enregistré | Doublon sur même jour | Vérifier l'historique |
| Notification non reçue | Paramètres notification | Vérifier les paramètres email |

### Raccourcis Clavier

| Action | Raccourci |
|--------|-----------|
| Tableau de bord | Alt + 1 |
| Notifications | Alt + 2 |
| Messages | Alt + 3 |
| Mon Profil | Alt + 4 |

---

## 16. API REST

### 16.1 Introduction
Le système dispose d'une API REST complète pour permettre l'intégration avec des applications mobiles ou d'autres systèmes.

**URL de base** : `http://127.0.0.1:8000/api/`

### 16.2 Authentification
L'API utilise l'authentification JWT (JSON Web Tokens).

**Connexion** :
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "votre_mot_de_passe"
}
```

**Réponse** :
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhb...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@ecole.com",
    "role": "superadmin"
  }
}
```

### 16.3 Utilisation du Token
Toutes les requêtes API doivent inclure le token dans l'en-tête :
```
Authorization: Bearer <votre_token>
```

### 16.4 Endpoints Principaux

#### Authentification
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/login/` | POST | Connexion |
| `/api/auth/token/refresh/` | POST | Rafraîchir token |
| `/api/auth/users/` | GET/POST | Utilisateurs |
| `/api/auth/users/me/` | GET | Profil utilisateur |
| `/api/auth/notifications/` | GET/POST | Notifications |
| `/api/auth/messages/` | GET/POST | Messages |
| `/api/auth/services/` | GET | Services |
| `/api/auth/modules/` | GET | Modules |

#### Élèves
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/eleves/eleves/` | GET/POST | Liste/Créer élèves |
| `/api/eleves/eleves/{id}/` | GET/PUT/DELETE | Détail/Modifier/Supprimer |
| `/api/eleves/parents/` | GET/POST | Parents/Tuteurs |
| `/api/eleves/inscriptions/` | GET/POST | Inscriptions |
| `/api/eleves/disciplines/` | GET/POST | Discipline |

#### Enseignement
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/academics/classes/` | GET/POST | Classes |
| `/api/academics/matieres/` | GET/POST | Matières |
| `/api/academics/evaluations/` | GET/POST | Évaluations |
| `/api/academics/examen/` | GET/POST | Examens |

#### Finances
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/finances/annees-scolaires/` | GET/POST | Années scolaires |
| `/api/finances/frais/` | GET/POST | Frais scolaires |
| `/api/finances/paiements/` | GET/POST | Paiements |
| `/api/finances/salaires/` | GET/POST | Salaires |

### 16.5 Exemple avec cURL
```bash
# Connexion
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Liste des élèves (avec token)
curl -X GET http://127.0.0.1:8000/api/eleves/eleves/ \
  -H "Authorization: Bearer <votre_token>"
```

---

## 17. Export de Données

### 17.1 Export Excel
Le système permet d'exporter les données sous format Excel.

**Chemins d'export** :
- **Élèves** : Scolarité → Élèves → Bouton Exporter
- **Paiements** : Finances → Paiements → Exporter
- **Personnel** : Ressources Humaines → Personnel → Exporter

**Format** : Fichier .xlsx avec mise en forme professionnelle
- En-têtes colorés
- Largeurs de colonnes ajustées
- Données triées

### 17.2 Export PDF
Génération de documents PDF pour :
- **Bulletins** : Rapports → Bulletins
- **Factures** : Finances → Factures
- **Reçus** : Finances → Paiements → Imprimer reçu

### 17.3 Personnalisation
Les exports peuvent être filtrés par :
- Période (date début/fin)
- Classe
- Statut

---

## 18. Notifications par Email

### 18.1 Configuration
Les emails automatiques nécessitent la configuration SMTP dans `settings.py` :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'
DEFAULT_FROM_EMAIL = 'noreply@ecole.com'
```

### 18.2 Types de Notifications Automatiques
| Type | Déclencheur | Destinataires |
|------|-------------|---------------|
| Confirmation inscription | Nouvel élève inscrit | Parent/Tuteur |
| Paiement reçu | Enregistrement paiement | Parent |
| Rappel paiement | Échéance proche | Parent |
| Bulletin disponible | Génération bulletin | Parent/Élève |

### 18.3 Envoi Manuel
1. Aller dans **Communication** → **Notifications**
2. Créer une nouvelle notification
3. Sélectionner les destinataires
4. Envoyer

---

## 19. Sauvegardes

### 19.1 Sauvegarde Manuelle
```bash
python manage.py backup
```

Options :
```bash
# Sauvegarde avec fichiers médias
python manage.py backup --media

# Sauvegarde avec fichiers statiques
python manage.py backup --static

# Sauvegarde complète avec nettoyage
python manage.py backup --media --static --clean 30
```

### 19.2 Fichiers de Sauvegarde
Les sauvegardes sont stockées dans le dossier `backups/` :
- `db_20260411_103045.sql.gz` - Base de données
- `media_20260411_103045.tar.gz` - Fichiers médias

### 19.3 Restauration
```bash
# Lister les sauvegardes
python manage.py backup

# La restauration se fait manuellement via pg_restore pour PostgreSQL
```

### 19.4 Planification (Avancé)
Pour une sauvegarde automatique quotidienne, ajouter au planificateur de tâches (cron) :
```bash
0 2 * * * cd /chemin/projet && python manage.py backup --media
```

---

## 20. Ressources Humaines - Congés et Absences

### 20.1 Types de Congés
**Chemin** : Admin Django → Ressources Humaines → Types de congés

**Types disponibles** :
- Congé annuel (jours payées)
- Congé maladie
- Congé exceptionnel
- Congé sans solde

### 20.2 Demande de Congé
1. Se connecter en tant que membre du personnel
2. Les demandes de congés se font via Admin Django
3. Ou via l'interface dédiée (si développée)

### 20.3 Gestion des Absences
**Chemin** : Admin Django → Ressources Humaines → Absences

**Types d'absences** :
- Maladie
- Accident
- Famille
- Autre

### 20.4 Soldes de Congés
Le système suit les soldes de congés par année et par employé.

---

## 21. Tableau de Bord Avancé

### 21.1 Statistiques par Rôle

| Métrique | Super Admin | Direction | Comptable | Professeur |
|---------|-------------|-----------|-----------|------------|
| Total élèves | ✓ | ✓ | - | - |
| Classes/Effectifs | ✓ | ✓ | - | - |
| Revenus/Charges | ✓ | ✓ | ✓ | - |
| Taux présence | ✓ | ✓ | - | ✓ |
| Notes moyennes | ✓ | ✓ | - | ✓ |

### 21.2 Indicateurs en Temps Réel
- Élèves actifs
- Paiements du jour
- Absences du jour
- Prochaines séances

---

## 22. Sécurités et Bonnes Pratiques

### 22.1 Gestion des Mot de Passe
- Minimum 8 caractères
- Changer régulièrement
- Ne pas réutiliser

### 22.2 2FA (Authentification à Deux Facteurs)
**Activation recommandée pour** :
- Direction
- Comptable
- Super Admin

### 22.3 Permissions
- Vérifier régulièrement les accès
- Supprimer les utilisateurs inactifs
- Limiter les droits au minimum nécessaire

### 22.4 Sauvegardes
- Sauvegarde quotidienne recommandée
- Vérifier la restauration régulièrement
- Stocker les sauvegardes sur un serveur distant

---

## Contact Support

Pour toute assistance technique :
- **Email** : support@syges-am.com
- **Téléphone** : +229 01 XX XX XX XX
- **Développeur** : ANANI M. Prince
- **Email développeur** : maounaananu0@gmail.com
- **WhatsApp** : +229 01 62 45 91 03 / +229 01 69 00 11 77

---

*Document généré pour le Système de Gestion Scolaire SyGeS-AM*
*Dernière mise à jour : Avril 2026*
*Version : 3.0*
