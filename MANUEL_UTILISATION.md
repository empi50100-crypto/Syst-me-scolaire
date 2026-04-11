# Manuel d'Utilisation - Système de Gestion Scolaire SyGeS-AM (V2)

## Table des Matières

1. [Introduction](#1-introduction)
2. [Rôles et Permissions](#2-rôles-et-permissions)
3. [Phase 1 : Configuration Initiale (Core)](#3-phase-1--configuration-initiale-core)
4. [Phase 2 : Gestion des Utilisateurs (Authentification)](#4-phase-2--gestion-des-utilisateurs-authentification)
5. [Phase 3 : Organisation Académique (Enseignement)](#5-phase-3--organisation-académique-enseignement)
6. [Phase 4 : Gestion des Élèves (Scolarité)](#6-phase-4--gestion-des-élèves-scolarité)
7. [Phase 5 : Suivi des Présences](#7-phase-5--suivi-des-présences)
8. [Phase 6 : Évaluations et Notes](#8-phase-6--évaluations-et-notes)
9. [Phase 7 : Ressources Humaines (RH)](#9-phase-7--ressources-humaines-rh)
10. [Phase 8 : Finances et Comptabilité](#10-phase-8--finances-et-comptabilité)
11. [Phase 9 : Rapports et Bulletins](#11-phase-9--rapports-et-bulletins)
12. [Phase 10 : Communication](#12-phase-10--communication)
13. [Flux de Travail Récapitulatifs](#13-flux-de-travail-récapitulatifs)
14. [Dépannage et Administration](#14-dépannage-et-administration)
15. [API REST](#15-api-rest)

---

## 1. Introduction

### 1.1 Accès au Système
- **URL locale** : `http://127.0.0.1:8000/`
- **Navigateurs compatibles** : Chrome, Firefox, Edge (versions récentes)
- **Base de données** : PostgreSQL (Migration effectuée depuis SQLite pour plus de robustesse)

### 1.2 Sécurité
- **Authentification 2FA** : Obligatoire pour les rôles Direction et Comptabilité.
- **Journal d'Audit** : Chaque action (création, modification, suppression) est tracée dans le `JournalAudit`.

---

## 2. Rôles et Permissions

### 2.1 Les Rôles du Système

| Rôle | Description |
|------|-------------|
| **Super Administrateur** | Accès total au système et à l'interface d'administration Django. |
| **Direction** | Gestion stratégique : configuration, RH, validation des rapports. |
| **Secrétariat** | Gestion opérationnelle : inscriptions, classes, documents élèves. |
| **Comptabilité** | Gestion financière : frais scolaires, paiements, salaires, caisse. |
| **Enseignement** | Espace Professeur : saisie des notes, appels, séances de cours. |
| **Surveillance** | Suivi disciplinaire : présences, retards, sanctions/récompenses. |

---

## 3. Phase 1 : Configuration Initiale (Core)

### 3.1 Paramétrage de base
**Chemin** : `Core` → `Années scolaires`
1. Créer l'**Année Scolaire** (ex: 2025-2026) et l'activer.
2. Définir les **Cycles** (Maternelle, Primaire, etc.).
3. Créer les **Niveaux Scolaires** rattachés aux cycles.
4. Configurer les **Périodes d'évaluation** (Trimestres ou Semestres).

---

## 4. Phase 2 : Gestion des Utilisateurs (Authentification)

### 4.1 Création des comptes
**Chemin** : `Authentification` → `Utilisateurs`
1. Créer un `Utilisateur` avec le rôle approprié.
2. **Approbation** : Les nouveaux comptes doivent être approuvés par la Direction.
3. **Permissions** : Utiliser les `Profils de Permissions` pour définir les accès par module.

---

## 5. Phase 3 : Organisation Académique (Enseignement)

### 5.1 Classes et Matières
- **Classes** : Créer les classes physiques rattachées à un niveau et une année scolaire.
- **Matières** : Liste globale des matières enseignées.
- **Salles** : Inventaire des salles de classe et équipements.

### 5.2 Corps Enseignant
- **Profils Professeurs** : Chaque enseignant doit avoir un `ProfilProfesseur` lié à son compte utilisateur.
- **Attributions** : Lier un professeur à une matière dans une classe spécifique.

---

## 6. Phase 4 : Gestion des Élèves (Scolarité)

### 6.1 Dossier Élève
- **Élèves** : Fiche complète avec matricule unique, photo et informations personnelles.
- **Parents/Tuteurs** : Coordonnées des responsables légaux.
- **Dossier Médical** : Allergies, groupe sanguin et contacts d'urgence.

### 6.2 Inscriptions et Discipline
- **Inscriptions** : Inscrire l'élève dans une classe pour l'année scolaire active.
- **Sanctions & Récompenses** : Suivi du comportement (remplace l'ancien module Discipline).
- **Conduite** : Calcul automatique de la note de conduite basée sur les incidents.

---

## 7. Phase 5 : Suivi des Présences

### 7.1 Séances de cours
- Le professeur démarre une **Séance** depuis son espace.
- L'**Appel** est effectué numériquement (Présent, Absent, Retard).
- Les **Statistiques** permettent de détecter les élèves décrocheurs.

---

## 8. Évaluations et Notes

### 8.1 Cycle des notes
1. **Examens** : Planification des évaluations (devoirs, compositions).
2. **Évaluations** : Saisie des notes individuelles par les professeurs.
3. **Fiches de notes** : Consultation des moyennes par élève/classe.
4. **Clôture** : Verrouillage des notes après validation.

---

## 9. Phase 7 : Ressources Humaines (RH)

### 9.1 Gestion des Employés
- **Personnel** : Fiche de poste, contrat et informations administratives de tout le personnel.
- **Salaires** : Génération des bulletins de paie mensuels.
- **Congés** : Suivi des absences et demandes de congés.

---

## 10. Phase 8 : Finances et Comptabilité

### 10.1 Flux Financiers
- **Frais Scolaires** : Paramétrage des montants par classe/niveau.
- **Paiements** : Encaissement des frais avec génération de reçu.
- **Caisse** : Suivi des entrées et sorties (Opérations de caisse).
- **Charges** : Gestion des dépenses de l'établissement (Loyer, Factures, Fournitures).

---

## 11. Phase 9 : Rapports et Bulletins

### 11.1 Documents Officiels
- **Bulletins** : Génération automatique des bulletins PDF à la fin des périodes.
- **Rapports Financiers** : Bilan des recettes et dépenses.
- **Statistiques Académiques** : Taux de réussite et classements.

---

## 12. Phase 10 : Communication

### 12.1 Outils Collaboratifs
- **Notifications** : Alertes système (nouveau paiement, absence signalée, etc.).
- **Messages** : Messagerie interne entre les membres du personnel.

---

## 13. Flux de Travail Récapitulatifs

### Rentrée Scolaire
1. Activer la nouvelle année (`Core`).
2. Mettre à jour les frais scolaires (`Finances`).
3. Inscrire les élèves (`Scolarité`).
4. Attribuer les classes aux professeurs (`Enseignement`).

### Fin de Trimestre
1. Saisir toutes les notes (`Enseignement`).
2. Clôturer la période (`Scolarité`).
3. Générer les bulletins (`Rapports`).

---

## 14. Dépannage et Administration

### Journal d'Audit
Toutes les actions critiques sont enregistrées. En cas d'erreur ou de litige, consulter le `JournalAudit` dans l'interface d'administration.

---

## 15. API REST

### Endpoints Principaux (V2)
- `/api/auth/` : Authentification et Profils.
- `/api/scolarite/` : Élèves, Inscriptions, Parents.
- `/api/enseignement/` : Classes, Matières, Évaluations.
- `/api/finances/` : Paiements, Frais, Factures.

---

*Document mis à jour : 11 Avril 2026*
*Version : 2.0 (Post-Refonte Architecture)*
