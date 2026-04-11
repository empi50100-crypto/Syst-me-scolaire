# GUIDE COMPLET DE TEST - Système de Gestion Scolaire SyGeS-AM (V2)

> Ce guide vous accompagne pas à pas pour tester toutes les fonctionnalités du système après la refonte architecturale.

---

## PRÉREQUIS

### Lancer le serveur
```bash
python manage.py runserver
```
- **URL** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/

### Créer un super utilisateur (Utilisateur)
```bash
python manage.py createsuperuser
```
*Note : Le modèle utilisateur personnalisé est `authentification.Utilisateur`.*

---

## ÉTAPE 1 : CONFIGURATION INITIALE (Application Core)

### 1.1 Initialiser les services et modules
```bash
python manage.py init_modules
```
**Vérification** : Se connecter et vérifier le menu latéral (Architecture 100% française).

### 1.2 Configurer l'année scolaire et les cycles
1. Se connecter en **Super Administrateur**
2. Aller dans **Core** > **Années scolaires** (ou Admin Django > Core)
3. Créer une année scolaire (ex: 2025-2026)
4. Cocher "Est active"
5. Créer les **Cycles** (Maternelle, Primaire, Collège, Lycée, Université)
6. Créer les **Niveaux Scolaires** (6ème, 5ème, etc.) et les **Périodes d'évaluation** (Trimestre 1, etc.)

---

## ÉTAPE 2 : GESTION DES UTILISATEURS (Authentification)

### 2.1 Créer les utilisateurs par rôle
1. Aller dans **Authentification** > **Utilisateurs**
2. Créer un `Utilisateur` pour chaque rôle :
   - **Direction** : rôle: Direction
   - **Secrétariat** : rôle: Secrétaire
   - **Comptabilité** : rôle: Comptable
   - **Enseignement** : rôle: Professeur
   - **Contrôle & Supervision** : rôle: Surveillance

### 2.2 Tester les connexions et le 2FA
1. Activer le **2FA** dans le profil utilisateur.
2. Se déconnecter et tester la connexion avec le code TOTP.
3. Vérifier que les menus s'adaptent au rôle choisi.

---

## ÉTAPE 3 : ORGANISATION ACADÉMIQUE (Enseignement)

### 3.1 Créer les classes
1. Aller dans **Enseignement** > **Classes**
2. Créer une classe (ex: "6ème A") en la liant à un **Niveau Scolaire** et une **Année Scolaire**.

### 3.2 Créer les matières
1. Aller dans **Enseignement** > **Matières**
2. Créer les matières (Mathématiques, Français, etc.).

### 3.3 Configurer les profils professeurs
1. Aller dans **Enseignement** > **Profils Professeurs**
2. Lier un `Utilisateur` (rôle Professeur) à un `ProfilProfesseur`.

### 3.4 Gérer les attributions
1. Aller dans **Enseignement** > **Attributions**
2. Affecter un `ProfilProfesseur` à une `Matiere` dans une `Classe`.

### 3.5 Gérer les salles
1. Aller dans **Enseignement** > **Salles**
2. Créer les salles de classe et laboratoires.

---

## ÉTAPE 4 : GESTION DES ÉLÈVES (Scolarité)

### 4.1 Enregistrer les élèves
1. Aller dans **Scolarité** > **Élèves**
2. Créer un `Eleve` (Matricule auto-généré `ELV...`).
3. Ajouter les **Parents/Tuteurs** et le **Dossier Médical**.

### 4.2 Inscriptions
1. Aller dans **Scolarité** > **Inscriptions**
2. Créer une `EleveInscription` pour lier l'élève à une `Classe` pour l'année en cours.

### 4.3 Discipline et Conduite
1. Enregistrer une **Sanction/Récompense** (anciennement Discipline).
2. Vérifier la mise à jour de la **Conduite Élève**.

---

## ÉTAPE 5 : SUIVI DES PRÉSENCES (Présences)

### 5.1 Séances et Appels
1. Se connecter en **Professeur**.
2. Créer une **Séance de cours**.
3. Effectuer l'**Appel** (Présent, Absent, Retard).
4. Vérifier les **Statistiques de présences**.

---

## ÉTAPE 6 : ÉVALUATIONS ET NOTES

### 6.1 Créer un examen
1. Aller dans **Enseignement** > **Examens**.
2. Créer un examen lié à une classe et une matière.

### 6.2 Saisie des notes
1. Saisir les notes via **Évaluations**.
2. Vérifier le calcul des moyennes dans les **Fiches de notes**.

### 6.3 Clôture
1. Tester la **Clôture de période** et la **Clôture des notes**.

---

## ÉTAPE 7 : FINANCES ET COMPTABILITÉ

### 7.1 Frais et Paiements
1. Créer des **Frais Scolaires** par classe ou niveau.
2. Enregistrer des **Paiements** pour les élèves.
3. Générer des **Factures**.

### 7.2 Caisse et Charges
1. Enregistrer des **Opérations de Caisse** (Encaissement/Décaissement).
2. Gérer les **Charges Fixes** (Loyer, Électricité) et **Opérationnelles**.

---

## ÉTAPE 8 : RESSOURCES HUMAINES (RH)

### 8.1 Personnel et Salaires
1. Créer un **Membre du Personnel** (lié à un `Utilisateur`).
2. Enregistrer les **Salaires** et générer les **Fiches de paie**.
3. Gérer les **Contrats** et les **Congés**.

---

## ÉTAPE 9 : RAPPORTS ET BULLETINS

### 9.1 Génération
1. Aller dans **Rapports** > **Bulletins**.
2. Générer le bulletin PDF d'un élève ou d'une classe.
3. Consulter les **Rapports Financiers**.

---

## ÉTAPE 10 : API REST (Postman / Curl)

### 10.1 Endpoints mis à jour
- **Auth** : `/api/auth/token/` (Obtenir JWT)
- **Scolarité** : `/api/scolarite/eleves/`, `/api/scolarite/inscriptions/`
- **Enseignement** : `/api/enseignement/classes/`, `/api/enseignement/matieres/`
- **Finances** : `/api/finances/paiements/`, `/api/finances/frais/`

---

## ÉTAPE 11 : ADMINISTRATION SYSTÈME

### 11.1 Audit et Logs
1. Vérifier le **Journal d'Audit** (JournalAudit) pour tracer les actions des utilisateurs.
2. Gérer les **Profils de Permissions** (ProfilPermission) et les **Permissions Personnalisées**.

---

## CHECKLIST DE RÉFÉRENCE

| # | Élément | Statut |
|---|---------|--------|
| 1 | Année Scolaire Active (Core) | ☐ |
| 2 | Utilisateurs & Rôles (Auth) | ☐ |
| 3 | Classes & Matières (Enseignement) | ☐ |
| 4 | Profils Professeurs & Attributions | ☐ |
| 5 | Inscriptions Élèves (Scolarité) | ☐ |
| 6 | Séances & Appels (Présences) | ☐ |
| 7 | Notes & Fiches de notes | ☐ |
| 8 | Paiements & Factures (Finances) | ☐ |
| 9 | Personnel & Salaires (RH) | ☐ |
| 10 | Journal d'Audit & Permissions | ☐ |

---

*Dernière mise à jour : 11 Avril 2026 (Post-Refonte Architecture)*
*Système : SyGeS-AM*
