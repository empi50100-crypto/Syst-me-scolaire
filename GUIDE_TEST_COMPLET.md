# GUIDE COMPLET DE TEST - Système de Gestion Scolaire SyGeS-AM

> Ce guide vous accompagne PAS À PAS pour tester toutes les fonctionnalités du système.
> Chaque étape indique : où cliquer, quoi saisir, et comment vérifier.

---

## PRÉREQUIS AVANT TOUT TEST

### 1. Lancer le serveur
1. Ouvrir un terminal dans le dossier `gestion_ecole`
2. Exécuter : `python manage.py runserver`
3. Ouvrir votre navigateur à : **http://127.0.0.1:8000/**

### 2. Identifiants de connexion
- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `admin2026`

---

## ÉTAPE 1 : CONNEXION ET ACCÈS AU TABLEAU DE BORD

### 1.1 Se connecter au système
1. Aller à : **http://127.0.0.1:8000/**
2. Vous êtes redirigé vers la page de connexion
3. Saisir :
   - **Nom d'utilisateur** : `admin`
   - **Mot de passe** : `admin2026`
4. Cliquer sur le bouton **[Se connecter]** (ou appuyez sur Entrée)
5. Vous accédez au **Tableau de bord**

### 1.2 Vérifier l'affichage du tableau de bord
1. Sur le tableau de bord, vérifier que :
   - Le message "Votre rôle n'est pas configuré" n'apparaît PLUS
   - Les **services** s'affichent dans le menu latéral à gauche
   - Vous voyez des sections comme "Scolarité", "Enseignement", "Finances", etc.

### 1.3 Navigation dans le menu latéral
1. Regardez le **menu à gauche** (sidebar)
2. Vous devez voir :
   - **Tableau de bord** (en haut)
   - Des **groupes de modules** dépliables :
     - Cliquez sur le petit triangle ▶ à côté d'un service pour déplier
     - Cliquez sur les **liens des modules** pour accéder aux fonctionnalités

---

## ÉTAPE 2 : CONFIGURATION DE L'ANNÉE SCOLAIRE

> L'interface web est accessible via le menu latéral. NE PAS utiliser l'administration Django (/admin/).

### 2.1 Créer une année scolaire
1. Dans le **menu latéral** (à gauche de l'écran), chercher le groupe **Core** ou **Configuration**
2. Cliquer sur le petit triangle ▶ à côté de **Core** pour déplier les modules
3. Cliquer sur **Années scolaires**
4. Cliquer sur le bouton **[Ajouter une année scolaire]**
5. Remplir le formulaire :
   - **Libellé** : `2025-2026` (saisir cette valeur)
   - **Date de début** : `2025-09-01` (cliquer sur le champ et sélectionner la date)
   - **Date de fin** : `2026-07-31` (cliquer sur le champ et sélectionner la date)
   - **Est active** : ☑ Cocher cette case
6. Cliquer sur **[Enregistrer]**
7. Vous revenez à la liste avec l'année créée

### 2.2 Créer des cycles pédagogiques
1. Dans le menu **Core**, cliquer sur **Cycles** (ou **Types de cycle**)
2. Cliquer sur **[Ajouter un cycle]**
3. Remplir :
   - **Année scolaire** : sélectionner `2025-2026`
   - **Type de cycle** : sélectionner `Trimestriel` ou `Semestriel`
   - **Numéro** : `1` (saisir)
   - **Date de début** : `2025-09-01`
   - **Date de fin** : `2025-12-31`
4. Cliquer sur **[Enregistrer]**
5. Répéter pour créer les autres périodes

### 2.3 Créer des niveaux scolaires
1. Dans le menu **Core**, cliquer sur **Niveaux scolaires**
2. Cliquer sur **[Ajouter un niveau]**
3. Remplir :
   - **Niveau** : sélectionner une valeur (ex: `6e` pour 6ème)
   - **Libellé** : `6ème` (saisir)
   - **Ordre** : `1` (saisir un nombre)
4. Cliquer sur **[Enregistrer]**
5. Répéter pour créer : `5ème` (ordre 2), `4ème` (ordre 3), etc.

### 2.4 Créer des périodes d'évaluation
1. Cliquer sur **Périodes d'évaluation** (ou **Périodes**)
2. Cliquer sur **[Ajouter une période]**
3. Remplir :
   - **Nom** : `Trimestre 1` (saisir)
   - **Date de début** : `2025-09-01`
   - **Date de fin** : `2025-12-31`
   - **Ordre** : `1`
4. Cliquer sur **[Enregistrer]**
5. Répéter pour : `Trimestre 2` (01/01/2026 - 31/03/2026), `Trimestre 3` (01/04/2026 - 31/07/2026)

---

## ÉTAPE 3 : CRÉATION DES UTILISATEURS

### 3.1 Créer un utilisateur de type Direction
1. Dans le menu latéral, chercher **Authentification**
2. Cliquer sur **Utilisateurs** (ou **Users**)
3. Cliquer sur le bouton **[Ajouter un utilisateur]**
4. Remplir le formulaire :
   - **Nom d'utilisateur** : `direction1` (saisir)
   - **Adresse email** : `direction@example.com` (saisir)
   - **Mot de passe** : `Direction2026!` (saisir)
   - **Confirmer le mot de passe** : `Direction2026!` (saisir)
   - **Prénom** : `Jean` (saisir)
   - **Nom** : `Dupont` (saisir)
   - **Rôle** : sélectionner `direction` dans la liste
   - **Est approuvé** : ☑ Cocher cette case
5. Cliquer sur **[Enregistrer]**

### 3.2 Créer un utilisateur de type Comptabilité
1. Répéter les étapes 3.1.1 à 3.1.3
2. Remplir :
   - **Nom d'utilisateur** : `comptable1`
   - **Email** : `comptable@example.com`
   - **Mot de passe** : `Comptable2026!`
   - **Rôle** : sélectionner `comptable`
   - **Est approuvé** : ☑ Cocher
3. Cliquer sur **[Enregistrer]**

### 3.3 Créer un utilisateur de type Secrétarial
1. Répéter les étapes 3.1.1 à 3.1.3
2. Remplir :
   - **Nom d'utilisateur** : `secretaire1`
   - **Email** : `secretaire@example.com`
   - **Mot de passe** : `Secretaire2026!`
   - **Rôle** : sélectionner `secretaire`
   - **Est approuvé** : ☑ Cocher
3. Cliquer sur **[Enregistrer]**

### 3.4 Créer un utilisateur de type Professeur
1. Répéter les étapes 3.1.1 à 3.1.3
2. Remplir :
   - **Nom d'utilisateur** : `professeur1`
   - **Email** : `professeur@example.com`
   - **Mot de passe** : `Professeur2026!`
   - **Rôle** : sélectionner `professeur`
   - **Est approuvé** : ☑ Cocher
3. Cliquer sur **[Enregistrer]**

---

## ÉTAPE 4 : CRÉATION DES CLASSES

### 4.1 Créer une classe
1. Dans le menu latéral, chercher **Enseignement**
2. Cliquer sur **Classes**
3. Cliquer sur le bouton **[Ajouter une classe]**
4. Remplir le formulaire :
   - **Nom** : `6ème A` (saisir)
   - **Niveau** : sélectionner `6ème` dans la liste
   - **Année scolaire** : sélectionner `2025-2026`
   - **Effectif maximum** : `30` (saisir)
5. Cliquer sur **[Enregistrer]**

### 4.2 Créer d'autres classes
1. Répéter l'étape 4.1 pour créer :
   - `6ème B` (même niveau)
   - `5ème A` (niveau 5ème)
   - `4ème A` (niveau 4ème)
   - `3ème A` (niveau 3ème)

---

## ÉTAPE 5 : CRÉATION DES MATIÈRES

### 5.1 Créer une matière
1. Dans le menu **Enseignement**, cliquer sur **Matières**
2. Cliquer sur **[Ajouter une matière]**
3. Remplir :
   - **Nom** : `Mathématiques` (saisir)
   - **Code** : `math` (saisir)
   - **Coefficient** : `4` (saisir)
4. Cliquer sur **[Enregistrer]**

### 5.2 Créer d'autres matières
1. Répéter pour créer :
   - **Français** (coefficient 4)
   - **Anglais** (coefficient 3)
   - **Histoire-Géo** (coefficient 2)
   - **Sciences Naturelles** (coefficient 2)
   - **Éducation Physique et Sportive** (coefficient 2)

---

## ÉTAPE 6 : CRÉATION DES PROFESSEURS (Profils Professeurs)

### 6.1 Créer un profil professeur
1. Dans **Enseignement**, cliquer sur **Profils Professeurs** (ou **Professeurs**)
2. Cliquer sur **[Ajouter un professeur]**
3. Remplir :
   - **Utilisateur** : sélectionner `professeur1` dans la liste
   - **Spécialité** : sélectionner `Mathématiques`
   - **Grade** : `Professeur Certifié` (saisir)
4. Cliquer sur **[Enregistrer]**

### 6.2 Créer d'autres profils
1. Créer les profils pour les autres professeurs :
   - Lier `professeur1` à **Français**
   - Créer un nouveau professeur avec `professeur1` et **Anglais**

---

## ÉTAPE 7 : ATTRIBUTION DES ENSEIGNEMENTS

### 7.1Attribuer une matière à une classe
1. Dans **Enseignement**, cliquer sur **Attributions**
2. Cliquer sur **[Ajouter une attribution]**
3. Remplir :
   - **Professeur** : sélectionner `professeur1` (ou le profil créé)
   - **Matière** : sélectionner `Mathématiques`
   - **Classe** : sélectionner `6ème A`
   - **Année scolaire** : sélectionner `2025-2026`
4. Cliquer sur **[Enregistrer]**

---

## ÉTAPE 8 : ENREGISTREMENT DES ÉLÈVES

### 8.1 Créer un élève
1. Dans le menu latéral, chercher **Scolarité**
2. Cliquer sur **Élèves**
3. Cliquer sur le bouton **[Ajouter un élève]**
4. Remplir le formulaire :
   - **Nom** : `Dupont` (saisir)
   - **Prénom** : `Marie` (saisir)
   - **Date de naissance** : `2014-05-15` (cliquer et sélectionner)
   - **Sexe** : sélectionner `Féminin`
   - **Lieu de naissance** : `Yaoundé` (saisir)
5. Cliquer sur **[Enregistrer]**

### 8.2 Inscrire l'élève dans une classe
1. Dans **Scolarité**, cliquer sur **Inscriptions**
2. Cliquer sur **[Ajouter une inscription]**
3. Remplir :
   - **Élève** : sélectionner `Dupont Marie`
   - **Classe** : sélectionner `6ème A`
   - **Année scolaire** : sélectionner `2025-2026`
   - **Date d'inscription** : `2025-09-01`
4. Cliquer sur **[Enregistrer]**

### 8.3 Inscrire plusieurs élèves
1. Répéter les étapes 8.1 et 8.2 pour créer et inscrire plusieurs élèves dans `6ème A`

---

## ÉTAPE 9 : GESTION DES PRÉSENCES

### 9.1 Créer une séance de cours
1. Se connecter en tant que **Professeur** (`professeur1`)
2. Dans le menu, cliquer sur **Mes séances** (ou **Séances de cours**)
3. Cliquer sur **[Créer une séance]**
4. Remplir :
   - ** Classe** : sélectionner `6ème A`
   - **Matière** : sélectionner `Mathématiques`
   - **Date** : `2025-10-15`
   - **Heure de début** : `08:00`
   - **Durée** : `60` (minutes)
5. Cliquer sur **[Enregistrer]**

### 9.2 Effectuer l'appel
1. Après créer la séance, vous êtes redirigé vers la page d'appel
2. Vous voyez la **liste des élèves** de la classe
3. Pour chaque élève, sélectionner son état :
   - **Présent** : Cliquer sur le bouton vert
   - **Absent** : Cliquer sur le bouton rouge
   - **Retard** : Cliquer sur le bouton orange
4. Cliquer sur **[Valider l'appel]**

### 9.3 Voir les statistiques
1. Dans le menu **Présences**, cliquer sur **Statistiques**
2. Vérifier les taux de présence par classe et par élève

---

## ÉTAPE 10 : ÉVALUATIONS ET NOTES

### 10.1 Créer un examen
1. Dans **Enseignement**, cliquer sur **Examens**
2. Cliquer sur **[Créer un examen]**
3. Remplir :
   - **Titre** : `Devoir surveillé 1` (saisir)
   - **Classe** : sélectionner `6ème A`
   - **Matière** : sélectionner `Mathématiques`
   - **Période** : sélectionner `Trimestre 1`
   - **Date** : `2025-10-20`
   - **Coefficient** : `1`
4. Cliquer sur **[Enregistrer]**

### 10.2 Saisir les notes
1. Dans la liste des examens, cliquer sur l'examen créé
2. Vous voyez la **table de saisie des notes**
3. Pour chaque élève, saisir la note sur 20 :
   - Dans le champ à côté du nom de l'élève, saisir la note (ex: `15`)
4. Cliquer sur **[Enregistrer les notes]**

### 10.3 Vérifier les fiches de notes
1. Dans **Enseignement**, cliquer sur **Fiches de notes**
2. Sélectionner une **classe** et une **matière**
3. Cliquer sur **[Générer la fiche]**
4. Vérifier que les moyennes sont calculées correctement

---

## ÉTAPE 11 : FINANCES - FRAIS SCOLAIRES

### 11.1 Créer des frais scolaires
1. Dans le menu **Finances**, cliquer sur **Frais scolaires**
2. Cliquer sur **[Ajouter des frais]**
3. Remplir :
   - **Libellé** : `Frais de Scolarité 2025-2026`
   - **Montant** : `50000` (saisir)
   - **Classe** : sélectionner `6ème A` (ou laisser vide pour tous)
   - **Année scolaire** : `2025-2026`
   - **Date d'échéance** : `2025-09-30`
4. Cliquer sur **[Enregistrer]**

### 11.2 Enregistrer un paiement
1. Dans **Finances**, cliquer sur **Paiements**
2. Cliquer sur **[Ajouter un paiement]**
3. Remplir :
   - **Élève** : sélectionner `Dupont Marie`
   - **Montant** : `50000`
   - **Date du paiement** : `2025-09-15`
   - **Mode de paiement** : sélectionner `Espèces` ou `Virement`
   - **Référence** : `PAI-001` (saisir)
4. Cliquer sur **[Enregistrer]**

### 11.3 Vérifier les factures
1. Dans **Finances**, cliquer sur **Factures**
2. Sélectionner un élève
3. Vérifier la facture générée automatiquement

---

## ÉTAPE 12 : FINANCES - CAISSE

### 12.1 Ouvrir la caisse
1. Dans **Finances**, cliquer sur **Caisse**
2. Cliquer sur **[Ouvrir la caisse]**
3. Saisir le **montant initial** : `100000`
4. Cliquer sur **[Valider]**

### 12.2 Enregistrer une opération
1. Dans la page Caisse, cliquer sur **[Nouvelle opération]**
2. Remplir :
   - **Type** : sélectionner `Encaissement` ou `Dépense`
   - **Montant** : `50000`
   - **Description** : `Paiement frais scolarité - Dupont Marie`
   - **Date** : `2025-09-15`
3. Cliquer sur **[Enregistrer]**

### 12.3 Voir le solde
1. Le **solde actuel** s'affiche en haut de la page
2. Vérifier que le solde est correct après les opérations

---

## ÉTAPE 13 : RESSOURCES HUMAINES

### 13.1 Créer un membre du personnel
1. Dans **Ressources Humaines**, cliquer sur **Personnel**
2. Cliquer sur **[Ajouter un membre]**
3. Remplir :
   - **Utilisateur** : laisser vide ou sélectionner un utilisateur
   - **Nom** : `Ondoua`
   - **Prénom** : `Pierre`
   - **Fonction** : `Agent d'entretien`
   - **Date d'embauche** : `2025-01-01`
   - **Salaire de base** : `50000`
4. Cliquer sur **[Enregistrer]**

### 13.2 Enregistrer un salaire
1. Dans **Ressources Humaines**, cliquer sur **Salaires**
2. Cliquer sur **[Ajouter un salaire]**
3. Remplir :
   - **Membre du personnel** : sélectionner `Ondoua Pierre`
   - **Mois** : `Septembre 2025`
   - **Salaire net** : `50000`
   - **Date de paiement** : `2025-09-30`
4. Cliquer sur **[Enregistrer]**

---

## ÉTAPE 14 : RAPPORTS ET BULLETINS

### 14.1 Générer un bulletin
1. Dans le menu **Rapports**, cliquer sur **Bulletins**
2. Sélectionner :
   - **Élève** : `Dupont Marie`
   - **Période** : `Trimestre 1`
   - **Classe** : `6ème A`
3. Cliquer sur **[Générer le bulletin]**
4. Un fichier PDF se télécharge - l'ouvrir pour vérifier

### 14.2 Générer un rapport financier
1. Dans **Rapports**, cliquer sur **Rapport financier**
2. Sélectionner la **période** : `Trimestre 1`
3. Cliquer sur **[Générer]**
4. Vérifier les totaux des encaissements et décaissements

---

## ÉTAPE 15 : TEST DES RÔLES

### 15.1 Tester le rôle Direction
1. Se déconnecter (cliquer sur votre nom en haut à droite puis **Déconnexion**)
2. Se reconnecter avec `direction1` / `Direction2026!`
3. Vérifier que :
   - Le menu affiche les modules accessibles à la Direction
   - Certain modules ne sont pas visibles (ex: Salaires)

### 15.2 Tester le rôle Comptabilité
1. Se déconnecter
2. Se reconnecter avec `comptable1` / `Comptable2026!`
3. Vérifier que :
   - Le menu affiche les modules de Finances
   - Les modules de RH ne sont pas visibles

### 15.3 Tester le rôle Professeur
1. Se déconnecter
2. Se reconnecter avec `professeur1` / `Professeur2026!`
3. Vérifier que :
   - Le menu affiche "Mes séances", "Mes classes", "Mes notes"
   - Les autres modules ne sont pas visibles

---

## VÉRIFICATION FINALE - CHECKLIST

| # | Tâche à vérifier | Où vérifier | Résultat attendu |
|---|------------------|--------------|-------------------|
| 1 | Connexion admin | Page login | Connexion réussie |
| 2 | Menu latéral fonctionne | Sidebar | 10 services affichés |
| 3 | Année scolaire créée | Core > Années | Année 2025-2026 active |
| 4 | Classes créées | Enseignement > Classes | 4+ classes |
| 5 | Matières créées | Enseignement > Matières | 5+ matières |
| 6 | Élèves créés | Scolarité > Élèves | 5+ élèves |
| 7 | Inscriptions créées | Scolarité > Inscriptions | Inscriptions ok |
| 8 | Appel effectué | Présences > Séances | Appel validé |
| 9 | Notes saisies | Enseignement > Examens | Notes ok |
| 10 | Paiement enregistré | Finances > Paiements | Paiement ok |
| 11 | Bulletin généré | Rapports > Bulletins | PDF généré |

---

## EN CAS DE PROBLÈME

### Erreurs courantes et solutions :

**1. "Votre rôle n'est pas configuré"**
- Solution : Vérifier que l'utilisateur a un **rôle** défini dans son profil

**2. Menu vide (pas de modules affichés)**
- Solution : Vérifier que les **modules** sont créés (commande `init_modules`)

**3. Erreur 500 lors de l'appel**
- Solution : Ouvrir le fichier `Erreur.txt` à la racine pour voir l'erreur exacte

**4. Impossible de créer un élève**
- Solution : Vérifier qu'une **année scolaire** active existe

---

*Dernière mise à jour : 11 Avril 2026*
*Système : SyGeS-AM*