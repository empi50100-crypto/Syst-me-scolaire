# GUIDE COMPLET DE TEST - Système de Gestion Scolaire SyGeS-AM

> Ce guide vous accompagne pas à pas pour tester toutes les fonctionnalités du système dans l'ordre chronologique.

---

## PRÉREQUIS

### Lancer le serveur
```bash
python manage.py runserver
```
- **URL** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/

### Créer un super utilisateur (si pas encore fait)
```bash
python manage.py createsuperuser
```

---

## ÉTAPE 1 : CONFIGURATION INITIALE

### 1.1 Initialiser les services et modules
```bash
python manage.py init_modules
```
**Vérification** : Se connecter et vérifier le menu latéral (10 services, 51 modules)

### 1.2 Configurer l'établissement
1. Se connecter en **Super Administrateur**
2. Aller dans **Configuration** > **Années scolaires**
3. Créer une année scolaire (ex: 2025-2026)
4. Cocher "Année active"

### 1.3 Configurer les paramètres
- Allers dans **Administration** > **Paramètres** (si disponible)
- Configurer le nom de l'établissement, logo, etc.

---

## ÉTAPE 2 : CRÉATION DES UTILISATEURS

### 2.1 Créer les utilisateurs par rôle
1. Aller dans **Administration** > **Utilisateurs**
2. Créer un utilisateur pour chaque rôle :
   - **Direction** : `directeur@ecole.com` (rôle: Direction)
   - **Secrétaire** : `secretaire@ecole.com` (rôle: Secrétaire)
   - **Comptable** : `comptable@ecole.com` (rôle: Comptabilité)
   - **Professeur** : `professeur@ecole.com` (rôle: Professeur)
   - **Surveillance** : `surveillance@ecole.com` (rôle: Surveillance)

### 2.2 Tester les connexions
Pour chaque utilisateur :
1. Se déconnecter
2. Se connecter avec les identifiants
3. Vérifier le menu latéral (modules accessibles)
4. Vérifier le dashboard (statistiques visibles)

---

## ÉTAPE 3 : GESTION ACADÉMIQUE (Enseignement)

### 3.1 Créer les niveaux scolaires
1. Se connecter en **Direction**
2. Aller dans **Enseignement** > **Classes**
3. Voir les niveaux disponibles (automatique depuis core)

### 3.2 Créer les classes
1. Cliquer sur **Nouvelle classe**
2. Remplir :
   - Nom : "6e Année A"
   - Niveau : "Sixième"
   - Année scolaire : 2025-2026
3. Répéter pour toutes les classes

### 3.3 Créer les matières
1. Aller dans **Enseignement** > **Matières**
2. Créer les matières par niveau :
   - Mathématiques, Français, Anglais, Histoire-Géo, Sciences, etc.

### 3.4 Créer les professeurs
1. Aller dans **Enseignement** > **Professeurs**
2. Créer un professeur (lier avec un utilisateur existant ou créer)

### 3.5 Créer les salles
1. Aller dans **Enseignement** > **Salles**
2. Créer les salles : "Salle 1", "Salle 2", "Amphithéâtre", etc.

### 3.6 Créer les attributions professeur-matière-classe
1. Aller dans **Enseignement** > **Attributions**
2. Affecter un professeur à une matière dans une classe

---

## ÉTAPE 4 : GESTION DES ÉLÈVES (Scolarité)

### 4.1 Créer les élèves
1. Se connecter en **Direction** ou **Secrétaire**
2. Aller dans **Scolarité** > **Élèves**
3. Cliquer sur **Nouvel élève**
4. Remplir :
   - Matricule : auto-généré
   - Nom, Prénom, Sexe, Date de naissance
   - Lieu de naissance
   - Photo (optionnel)
5. **Répéter** pour plusieurs élèves (minimum 5-10 pour tester)

### 4.2 Créer les parents/tuteurs
1. Dans la fiche élève, section **Parents**
2. Ajouter un parent/tuteur :
   - Nom, Prénom
   - Relation (Père, Mère, Tuteur)
   - Téléphone, Email, Profession
   - Adresse

### 4.3 Inscrire les élèves aux classes
1. Aller dans **Scolarité** > **Inscriptions**
2. Pour chaque élève :
   - Sélectionner la classe
   - Confirmer l'inscription

### 4.4 Gérer les documents
1. Dans la fiche élève > **Documents**
2. Ajouter : Acte de naissance, Photo, etc.

---

## ÉTAPE 5 : EMPLOI DU TEMPS

### 5.1 Définir les contraintes horaires
1. Aller dans **Enseignement** > **Contraintes horaires**
2. Créer les contraintes :
   - Cours magistral le matin
   - Pas de cours le mercredi après-midi
   - etc.

### 5.2 Générer l'emploi du temps
1. Cliquer sur **Générer emploi du temps**
2. Vérifier les enseignements attribués
3. Confirmer la génération

### 5.3 Consulter l'emploi du temps
1. **Direction** : Voir tout l'emploi du temps
2. **Professeur** : Voir ses propres cours

---

## ÉTAPE 6 : GESTION DES PRÉSENCES

### 6.1 Démarrer une séance de cours
1. Se connecter en **Professeur**
2. Aller dans **Espace Enseignant** > **Mes Séances**
3. Cliquer sur **Démarrer** pour une séance

### 6.2 Effectuer l'appel
1. Liste des élèves de la classe
2. Marquer : Present, Absent, Retard
3. Ajouter des observations

### 6.3 Consulter les statistiques
1. Aller dans **Présences** > **Statistiques**
2. Voir : Taux d'absence, Retards par classe, etc.

---

## ÉTAPE 7 : ÉVALUATIONS ET NOTES

### 7.1 Créer un examen
1. Se connecter en **Direction** ou **Professeur**
2. Aller dans **Enseignement** > **Examens**
3. Créer un examen :
   - Nom : "Devoir Maths 1er trimestre"
   - Classe : 6e Année A
   - Matière : Mathématiques
   - Date, Durée, Coefficient

### 7.2 Saisie des notes
1. Aller dans **Espace Enseignant** > **Saisie Notes**
2. Sélectionner l'examen
3. Saisir les notes pour chaque élève

### 7.3 Clôturer les périodes
1. Aller dans **Scolarité** > **Clôture Périodes**
2. Clôturer le 1er trimestre

---

## ÉTAPE 8 : BULLETINS ET RAPPORTS

### 8.1 Générer les bulletins
1. Se connecter en **Direction**
2. Aller dans **Rapports** > **Bulletins**
3. Sélectionner la classe et la période
4. Cliquer sur **Générer**

### 8.2 Consulter les fiches de notes
1. Aller dans **Scolarité** > **Fiches de Notes**
2. Voir les moyennes par élève

### 8.3 Rapports académiques
1. Aller dans **Rapports** > **Rapport Académique**
2. Voir les statistiques globales

---

## ÉTAPE 9 : FINANCES

### 9.1 Créer les frais scolaires
1. Se connecter en **Direction** ou **Comptable**
2. Aller dans **Finances** > **Frais Scolaires**
3. Créer :
   - Type : Frais de scolarité
   - Montant : 150000 CFA
   - Tranche : 1er, 2nd, 3ème

### 9.2 Enregistrer les paiements
1. Aller dans **Finances** > **Paiements**
2. Sélectionner l'élève
3. Saisir :
   - Montant
   - Mode : Espèces, Chèque, Virement
   - Date
   - Référence

### 9.3 Tableau de bord financier
1. Aller dans **Finances** > **Tableau de Bord**
2. Voir :
   - Total encaissé
   - Montant restant à payer
   - Élèves en retard

### 9.4 Gestion des charges
1. Aller dans **Finances** > **Charges**
2. Ajouter : Salaires, Fournitures, Entretien

### 9.5 Export Excel des paiements
1. Tester l'export dans les vues finances

---

## ÉTAPE 10 : RESSOURCES HUMAINES

### 10.1 Gestion du personnel
1. Se connecter en **Direction**
2. Aller dans **Ressources Humaines** > **Personnel**
3. Créer un membre du personnel

### 10.2 Gestion des salaires
1. Aller dans **Ressources Humaines** > **Salaires**
2. Enregistrer un salaire mensuel

### 10.3 Fiches de postes
1. Aller dans **Ressources Humaines** > **Postes**
2. Créer des postes à pourvoir

### 10.4 Gestion des congés
1. **Optionnel** : Tester les modèles de congés
2. Admin Django > Ressources Humaines > Congés

---

## ÉTAPE 11 : COMMUNICATION

### 11.1 Notifications
1. Aller dans **Communication** > **Notifications**
2. Créer une notification pour les utilisateurs

### 11.2 Messages
1. Aller dans **Communication** > **Messages**
2. Envoyer un message à un autre utilisateur

---

## ÉTAPE 12 : API REST

### 12.1 Tester les endpoints
1. Installer **Postman** ou utiliser **curl**
2. Endpoint de base : `http://127.0.0.1:8000/api/`

### 12.2 Authentification
```
POST /api/auth/login/
{
  "username": "admin",
  "password": "motdepasse"
}
```
**Réponse** : Token JWT

### 12.3 Utiliser le token
```
Authorization: Bearer <token>
```

### 12.4 Endpoints principaux
- `/api/auth/users/` - Liste des utilisateurs
- `/api/auth/notifications/` - Notifications
- `/api/eleves/eleves/` - Élèves
- `/api/academics/classes/` - Classes
- `/api/finances/paiements/` - Paiements

---

## ÉTAPE 13 : EXPORT ET SAUVEGARDES

### 13.1 Export Excel
Tester l'export des :
- Élèves
- Paiements
- Personnel

### 13.2 Sauvegarde base de données
```bash
python manage.py backup
```

---

## ÉTAPE 14 : ADMINISTRATION

### 14.1 Gestion des permissions
1. Aller dans **Administration** > **Permissions**
2. Modifier les permissions d'un utilisateur

### 14.2 Demandes d'approbation
1. Certaines actions nécessitent une approbation
2. Tester le flux d'approbation

### 14.3 Admin Django
1. Aller dans **Administration** > **Admin Django**
2. Accès complet à toutes les tables

---

## CHECKLIST DE TEST

| # | Service | Tâche | Statut |
|---|---------|-------|--------|
| 1 | Config | Année scolaire créée | ☐ |
| 2 | Config | Utilisateurs créés | ☐ |
| 3 | Enseignement | Classes créées | ☐ |
| 4 | Enseignement | Matières créées | ☐ |
| 5 | Enseignement | Professeurs créés | ☐ |
| 6 | Enseignement | Salles créées | ☐ |
| 7 | Enseignement | Attributions faites | ☐ |
| 8 | Scolarité | Élèves créés | ☐ |
| 9 | Scolarité | Parents ajoutés | ☐ |
| 10 | Scolarité | Inscriptions effectuées | ☐ |
| 11 | Présences | Séance démarrée | ☐ |
| 12 | Présences | Appel effectué | ☐ |
| 13 | Notes | Examen créé | ☐ |
| 14 | Notes | Notes saisies | ☐ |
| 15 | Rapports | Bulletins générés | ☐ |
| 16 | Finances | Frais créés | ☐ |
| 17 | Finances | Paiements enregistrés | ☐ |
| 18 | RH | Personnel créé | ☐ |
| 19 | RH | Salaire enregistré | ☐ |
| 20 | Comm | Notification envoyée | ☐ |
| 21 | Comm | Message envoyé | ☐ |
| 22 | API | Token obtenu | ☐ |
| 23 | API | Endpoint testé | ☐ |
| 24 | Export | Excel généré | ☐ |
| 25 | Backup | Sauvegarde créée | ☐ |

---

## ERREURS COURANTES ET SOLUTIONS

### Erreur : "Aucun module nommé"
```bash
python manage.py check
```

### Erreur : Base de données
```bash
python manage.py migrate
python manage.py init_modules
```

### Erreur : Permissions
Vérifier dans Admin Django > Permissions que les rôles sont bien configurés

---

*Document mis à jour : Avril 2026*
*Système : SyGeS-AM - Gestion Scolaire*