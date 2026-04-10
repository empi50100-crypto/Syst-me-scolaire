# SYSTÈME DE GESTION SCOLAIRE - DOCUMENTATION COMPLÈTE

## 1. PRÉSENTATION DU PROJET

### 1.1 Scénario

Ce projet est un **système de gestion d'établissement scolaire complet** développé en Django (Python). Il permet de gérer toutes les aspects d'une école :

- Inscription et suivi des élèves
- Gestion académique (classes, matières, professeurs, enseignements, notes, examens)
- Suivi des présences
- Gestion financière (frais scolaires, paiements, salaires, charges, factures)
- Génération de rapports et bulletins

L'application est conçue pour gérer un établissement scolaire de la maternelle jusqu'à l'université, avec plusieurs rôles d'utilisateurs.

### 1.2 Caractéristiques techniques

- **Framework** : Django 4.x
- **Base de données** : SQLite3 (modifiable pour PostgreSQL/MySQL)
- **API REST** : Django REST Framework
- **Authentification** : JWT + 2FA (TOTP)
- **Langue** : Français
- **Fuseau horaire** : Africa/Douala

---

## 2. RÔLES D'UTILISATEURS

| Code | Nom | Description |
|------|-----|-------------|
| `superadmin` | Super Administrateur | Accès total au système, gestion complète |
| `direction` | Direction générale | Gestion stratégique, approbation des demandes |
| `secretaire` | Secregistrement | Accueil, inscriptions, gestion quotidienne |
| `comptable` | Comptabilité | Gestion finances, paiements, salaires |
| `professeur` | Enseignement | Saisie notes, évaluations, présence en classe |
| `surveillance` | Contrôle & Surveillance | Suivi discipline, présences |
| `agent_securite` | Agent de Sécurité | Sécurité de l'établissement |
| `responsable_stock` | Responsable Stock | Gestion stocks et fournitures |
| `chauffeur` | Chauffeur | Transport scolaire |
| `responsable_stock` | Responsable Stock | Gestion inventaire |

---

## 3. ARCHITECTURE DES SERVICES (APPS)

Le projet contient 7 applications Django principales :

| App | Objectif principal | Modèles principaux |
|-----|-------------------|-------------------|
| `accounts` | Authentification, utilisateurs, permissions | User, Service, Module, Permission, Notification, Message, AuditLog |
| `eleves` | Gestion des élèves | Eleve, ParentTuteur, Inscription, DisciplineEleve, DossierMedical |
| `academics` | Gestion académique | Classe, Matiere, Professeur, Enseignement, Evaluation, Examen, Salle |
| `presences` | Suivi des présences | Presence, Appel, SeanceCours |
| `finances` | Gestion financière | AnneeScolaire, FraisScolaire, Paiement, Personnel, Salaire, ChargeFixe, Facture |
| `rapports` | Génération rapports | Bulletin |
| `core` | Configuration centrale | Settings, URLs, Middleware |

---

## 4. MODÈLES DE DONNÉES (DATABASE)

### 4.1 accounts - Gestion des utilisateurs

#### User (Utilisateur)
- **Champs** : username, email, role, telephone, adresse, eleve (lien parent), is_approved, salaire_base, date_embauche, matiere
- **Méthodes** : is_superadmin(), is_direction(), is_secretaire(), is_comptable(), is_professeur(), is_surveillance()

#### Service (Service)
- **Champs** : nom, code, description, icon, ordre, est_actif
- **Description** : Représente un service de l'application (ex: Academics, Finances)

#### Module (Module/Sous-module)
- **Champs** : service, nom, code, url, icon, type_module, parent, ordre, est_actif
- **Description** : Sous-modules accessibles dans chaque service

#### Permission (Permission par rôle)
- **Champs** : module, role, actions (JSON), niveau, require_approval, approbateurs (JSON)

#### PermissionUtilisateur (Permission personnalisée)
- **Champs** : utilisateur, module, actions (JSON), niveau, date_debut, date_fin, est_temporaire, est_actif

#### Notification (Notification)
- **Champs** : destinataire, expediteur, type_notification, titre, message, lien, est_lu

#### Message (Message interne)
- **Champs** : auteur, destinataire, type_message, service, sujet, contenu, est_lu, groupe

#### AuditLog (Journal d'audit)
- **Champs** : user, action, model, object_id, object_repr, details, ip_address, annee_scolaire

#### DemandeApprobation (Demande d'approbation)
- **Champs** : demandeur, approbateur, type_action, type_objet, objet_id, details, statut

#### LoginAttempt (Tentative de connexion)
- **Champs** : username, ip_address, attempts, lock_count, locked_until

#### PasswordResetCode (Code de réinitialisation)
- **Champs** : user, code, expires_at, used

#### Groupe (Groupe)
- **Champs** : nom, description
- **Types** : direction, secretaire, comptable, professeur, surveillance

#### RoleQuota (Quota par rôle)
- **Champs** : role, max_users, description
- **Description** : Limite le nombre d'utilisateurs par rôle

#### PermissionModification (Modification de permission)
- **Champs** : permission, module, role, actions_avant, actions_apres, niveau_avant, niveau_apres, type_modification, motif, demandeur, approbateur, statut, date_decision, commentaire
- **Description** : Gère les demandes de modification de permissions avec workflow d'approbation

#### ModulePermission (Profil de permissions)
- **Champs** : nom, description, modules, roles_cibles (JSON)
- **Description** : Permet de créer des profils de permissions réutilisables

---

### 4.2 eleves - Gestion des élèves

#### Eleve (Élève)
- **Champs** : matricule, nom, prenom, date_naissance, lieu_naissance, sexe, adresse, telephone_parent, email_parent, photo, statut, niveau, observations
- **Statuts** : actif, ancien, suspendu, radié
- **Niveaux** : Maternelle 1 à Université (Master 2)

#### ParentTuteur (Parent/Tuteur)
- **Champs** : eleve, nom, prenom, lien_parente, telephone, whatsapp, email, profession, adresse, est_contact_principal

#### DossierMedical (Dossier médical)
- **Champs** : eleve, groupe_sanguin, allergies, traitements_en_cours, vaccinations, allergies_medicamenteuses, maladies_chroniques, contacts_urgence, medecin_traitant

#### Inscription (Inscription)
- **Champs** : eleve, classe, annee_scolaire, date_inscription, rang, moyenne_generale, mention, decision

#### DisciplineEleve (Discipline)
- **Champs** : eleve, inscription, type, type_detail, description, date_incident, periode, est_signale, points, traite_par, service_traitant, date_traitement

#### PeriodeCloture (Clôture de période)
- **Champs** : classe, periode, cloture_par, observations

#### NotePeriodeCloture (Clôture de notes)
- **Champs** : classe, professeur, periode, cloture_par, observations

#### ConduiteConfig (Configuration conduite)
- **Champs** : annee_scolaire, niveau, note_base, cree_par

#### ConduiteEleve (Conduite élève)
- **Champs** : inscription, note_base, total_deductions, total_recompenses, note_finale

#### DocumentEleve (Document élève)
- **Champs** : eleve, type_document, fichier, description

---

### 4.3 academics - Gestion académique

#### Classe (Classe)
- **Champs** : nom, niveau, serie, domaine, subdivision, annee_scolaire, capacite, professeur_principal, note_conduite_base, matieres, eleves
- **Niveaux** : Maternelle1 → Université (D3)
- **Séries** : TC, A1, A2, C, D, G1, G2, E, F
- **Domaines** : Sciences, SVT, Economie, Droit, Lettres, Education, Santé, Communication

#### Matiere (Matière)
- **Champs** : nom, coefficient

#### CoefficientMatiere (Coefficient matière)
- **Champs** : classe, matiere, coefficient

#### Salle (Salle)
- **Champs** : nom, type_salle, capacite, etage, equipements, est_disponible

#### ClasseMatiere (Matière assignée à classe)
- **Champs** : classe, matiere, coefficient

#### Examen (Examen)
- **Champs** : nom, type_examen, annee_scolaire, classe, matiere, date_examen, duree_minutes, note_sur, coefficient, lieu, surveillant, instructions, est_publie

#### Epreuve (Épreuve d'examen)
- **Champs** : examen, eleve, note, appreciation, est_corrige, date_correction, corrige_par

#### Profess:eur (Professeur)
- **Champs** : user, nom, prenom, email, telephone, date_embauche, statut, salaire_base
- **Statuts** : actif, conge, parti

#### Enseignement (Enseignement)
- **Champs** : professeur, classe, matiere, annee_scolaire, horaires (JSON)

#### ContrainteHoraire (Contrainte horaire)
- **Champs** : professeur, jour, heure_debut, heure_fin, type_contrainte, motif, est_recurrent, date_fin, statut

#### Evaluation (Évaluation/Note)
- **Champs** : eleve, matiere, type_eval, titre, date_eval, note, coefficient, annee_scolaire, observations, periode
- **Types** : interrogation, mini_devoir, devoir, examen

#### FicheNote (Fiche de note)
- **Champs** : eleve, matiere, cycle, moyenne, rang, appreciation

---

### 4.4 presences - Suivi des présences

#### Presence (Présence)
- **Champs** : eleve, classe, date, heure_appel, statut, motif_absence, justifie, professeur, annee_scolaire
- **Statuts** : present, absent, retard

#### Appel (Appel)
- **Champs** : classe, date, heure_debut, heure_fin, professeur, matiere, annee_scolaire

#### SeanceCours (Séance de cours)
- **Champs** : professeur, classe, matiere, date, heure_debut, heure_fin, duree_minutes, statut, annee_scolaire, notes, creee_par
- **Statuts** : en_cours, terminee, annulee

---

### 4.5 finances - Gestion financière

#### AnneeScolaire (Année scolaire)
- **Champs** : libelle, date_debut, date_fin, est_active, type_cycle_actif
- **Types cycles** : trimestriel, semestriel

#### CycleConfig (Configuration cycle)
- **Champs** : annee_scolaire, type_cycle, numero, date_debut, date_fin, pourcentage

#### FraisScolaire (Frais scolaire)
- **Champs** : type_frais, mode_application, classe, niveau, filiere, annee_scolaire, montant, description
- **Types frais** : inscription, scolarite, bibliotheque, activites, transport, cantine, autre
- **Modes** : general, niveau, detaille

#### Paiement (Paiement)
- **Champs** : eleve, frais, date_paiement, montant, mode_paiement, reference, personnel, observations
- **Modes paiement** : espece, virement, mobile_money, cheque

#### EcoleCompte (Opération de caisse)
- **Champs** : date_operation, type_operation, categorie, montant, beneficiaire, motif, personnel
- **Types** : encaissement, decaissement

#### ChargeFixe (Charge fixe)
- **Champs** : nom, type_charge, montant, periodicite, beneficiaire, description, est_active, date_debut, date_fin

#### ChargeOperationnelle (Charge opérationnelle)
- **Champs** : date_charge, type_charge, description, montant, fournisseur, reference, personnel, est_payee, date_paiement

#### Personnel (Personnel)
- **Champs** : nom, prenom, fonction, telephone, adresse, salaire_mensuel, date_embauche, est_actif, compte_utilisateur, observations

#### Salaire (Salaire)
- **Champs** : personnel, mois, annee, salaire_brut, retenues, salaire_net, date_versement, est_paye

#### Rappel (Rappel de paiement)
- **Champs** : eleve, type_rappel, date_echeance, montant_due, montant_paye, statut, date_acquittement, observations

#### Facture (Facture)
- **Champs** : eleve, inscription, numero_facture, date_facture, date_echeance, montant_total, montant_paye, statut, personnel, observations

#### LigneFacture (Ligne de facture)
- **Champs** : facture, frais, description, quantite, prix_unitaire, remise

#### BourseRemise (Bourse/Remise)
- **Champs** : nom, type_remise, pourcentage, description, est_active, date_debut, date_fin

#### EleveBourse (Élève boursier)
- **Champs** : eleve, bourse, annee_scolaire, pourcentage_accorde, justification, est_active

#### CategorieDepense (Catégorie de dépense)
- **Champs** : nom, description, est_active

#### RapportFinancier (Rapport financier)
- **Champs** : type_rapport, annee_scolaire, date_debut, date_fin, total_recettes, total_depenses, total_salaires, solde, details_recettes, details_depenses, genere_par

---

### 4.6 rapports - Génération de rapports

#### Bulletin (Bulletin scolaire)
- **Champs** : eleve, inscription, cycle, periode, date_generation, moyenne_generale, rang, mention, appreciation, pdf_file

---

## 5. LISTE COMPLÈTE DES PAGES (URLs)

### 5.1 ACCUEIL ET AUTHENTIFICATION

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/` | home | **Accueil** | Page d'accueil publique |
| `/dashboard/` | dashboard | **Tableau de bord** | Dashboard personnalisé selon le rôle |
| `/accounts/login/` | login | **Connexion** | Formulaire de connexion |
| `/accounts/register/` | register | **Inscription** | Création de compte utilisateur |
| `/accounts/logout/` | logout | **Déconnexion** | Déconnexion |
| `/accounts/password-recovery/` | password_recovery | **Récupération mot de passe** | Demander un code de réinitialisation |
| `/accounts/password-recovery/verify/` | password_recovery_verify | **Vérifier le code** | Entrer le code reçu par email |
| `/accounts/password-recovery/reset/` | password_recovery_reset | **Nouveau mot de passe** | Définir nouveau mot de passe |
| `/accounts/profile/` | profile | **Mon profil** | Modifier mon profil utilisateur |
| `/accounts/2fa/setup/` | two_factor_setup | **Configuration 2FA** | Activer l'authentification à deux facteurs |

---

### 5.2 GESTION DES UTILISATEURS (`/accounts/users/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/accounts/users/` | user_list | **Liste des utilisateurs** | Voir tous les utilisateurs du système |
| `/accounts/users/ajouter/` | user_create | **Ajouter un utilisateur** | Créer un nouvel utilisateur |
| `/accounts/users/<int:pk>/` | user_edit | **Modifier l'utilisateur** | Éditer un utilisateur existant |
| `/accounts/users/<int:pk>/supprimer/` | user_delete | **Supprimer l'utilisateur** | Supprimer un utilisateur |
| `/accounts/users/<int:pk>/toggle/` | user_toggle_active | **Activer/Désactiver** | Activer ou désactiver un compte |
| `/accounts/users/<int:pk>/approuver/` | user_approve | **Approuver l'utilisateur** | Approuver un compte en attente |
| `/accounts/users/<int:pk>/password/` | user_show_password | **Voir le mot de passe** | Afficher le mot de passe temporaire |
| `/accounts/users/<int:pk>/password/reset/` | user_reset_password | **Réinitialiser le mot de passe** | Réinitialiser le mot de passe |

---

### 5.3 NOTIFICATIONS ET MESSAGES (`/accounts/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/accounts/notifications/` | notification_list | **Mes notifications** | Liste des notifications |
| `/accounts/notifications/<int:pk>/` | notification_detail | **Détail notification** | Voir une notification |
| `/accounts/notifications/marquer-tout/` | notification_mark_all_read | **Tout marquer comme lu** | Marquer toutes comme lues |
| `/accounts/messages/` | message_list | **Mes messages** | Liste des messages reçus |
| `/accounts/messages/nouveau/` | message_create | **Nouveau message** | Envoyer un nouveau message |
| `/accounts/messages/<int:pk>/` | message_detail | **Détail du message** | Lire un message |
| `/accounts/messages/marquer-tout/` | message_mark_all_read | **Tout marquer comme lu** | Marquer tous comme lus |
| `/accounts/chat/` | chat_inbox | **Messagerie** | Boîte de réception chat |
| `/accounts/chat/nouveau/` | chat_new | **Nouvelle conversation** | Démarrer une nouvelle conversation |
| `/accounts/chat/<int:user_id>/` | chat_conversation | **Conversation** | Discussion avec un utilisateur |

---

### 5.4 DEMANDES D'APPROBATION (`/accounts/demandes/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/accounts/demandes/` | demande_list | **Demandes d'approbation** | Liste des demandes en attente |
| `/accounts/demandes/<int:pk>/` | demande_detail | **Détail de la demande** | Voir une demande |
| `/accounts/demandes/<int:pk>/approuver/` | demande_approuver | **Approuver** | Approuver une demande |
| `/accounts/demandes/<int:pk>/rejeter/` | demande_rejeter | **Rejeter** | Rejeter une demande |

---

### 5.5 GESTIONS SPÉCIALES (`/accounts/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/accounts/comptes-bloques/` | locked_accounts | **Comptes bloqués** | Liste des comptes verrouillés |
| `/accounts/comptes-bloques/<str:username>/deverrouiller/` | unlock_account | **Déverrouiller** | Déverrouiller un compte |
| `/accounts/permissions-modifications/` | permission_modification_list | **Modifications de permissions** |Historique des modifications |
| `/accounts/permissions-modifications/<int:pk>/` | permission_modification_detail | **Détail modification** | Voir les détails |
| `/accounts/permissions-modifications/<int:pk>/approuver/` | permission_modification_approuver | **Approuver modification** | Approuver une modification |
| `/accounts/permissions-modifications/<int:pk>/rejeter/` | permission_modification_rejeter | **Rejeter modification** | Rejeter une modification |
| `/accounts/permissions-utilisateur/` | permission_utilisateur_list | **Permissions utilisateurs** | Liste des permissions personnalisées |
| `/accounts/permissions-utilisateur/ajouter/` | permission_utilisateur_create | **Ajouter permission** | Créer une permission personnalisée |
| `/accounts/permissions-utilisateur/<int:pk>/modifier/` | permission_utilisateur_edit | **Modifier permission** | Modifier une permission |
| `/accounts/permissions-utilisateur/<int:pk>/supprimer/` | permission_utilisateur_delete | **Supprimer permission** | Supprimer une permission |
| `/accounts/utilisateur/<int:user_id>/permissions/` | user_permissions_detail | **Permissions utilisateur** | Voir les permissions d'un utilisateur |
| `/accounts/utilisateur/<int:user_id>/permissions/<str:module_code>/` | user_permission_toggle | **Basculer permission** | Activer/désactiver une permission |

---

### 5.6 GESTION DES ÉLÈVES (`/eleves/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/` | eleve_list | **Liste des élèves** | Voir tous les élèves |
| `/eleves/ajouter/` | eleve_create | **Ajouter un élève** | Inscrire un nouvel élève |
| `/eleves/<int:pk>/` | eleve_detail | **Profil de l'élève** | Détails du profil élève |
| `/eleves/<int:pk>/modifier/` | eleve_update | **Modifier l'élève** | Modifier les informations |
| `/eleves/<int:pk>/supprimer/` | eleve_delete | **Supprimer l'élève** | Supprimer un élève |

---

### 5.7 GESTION DES PARENTS/TUTEURS (`/eleves/parents/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/parents/` | parent_list | **Liste des parents/tuteurs** | Tous les parents/tuteurs |
| `/eleves/parents/ajouter/` | parent_create | **Ajouter un parent** | Créer un nouveau parent/tuteur |
| `/eleves/parents/ajouter/<int:eleve_id>/` | parent_create_eleve | **Ajouter parent pour élève** | Ajouter un parent pour un élève spécifique |

---

### 5.8 DOSSIERS MÉDICAUX (`/eleves/dossiers-medicaux/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/dossiers-medicaux/` | dossiers_medical | **Dossiers médicaux** | Liste des dossiers médicaux |
| `/eleves/dossiers-medicaux/<int:eleve_id>/` | dossier_medical_edit | **Modifier dossier médical** | Éditer le dossier médical |

---

### 5.9 DOCUMENTS (`/eleves/documents/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/documents/` | documents_eleve | **Documents des élèves** | Liste des documents uploadés |
| `/eleves/documents/<int:eleve_id>/ajouter/` | document_upload | **Télécharger un document** | Uploader un document |
| `/eleves/documents/<int:pk>/supprimer/` | document_delete | **Supprimer document** | Supprimer un document |

---

### 5.10 DISCIPLINE (`/eleves/discipline/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/discipline/` | discipline_list | **Liste des disciplines** | Historique des sanctions/récompenses |
| `/eleves/discipline/ajouter/` | discipline_create | **Ajouter une discipline** | Enregistrer une sanction/récompense |
| `/eleves/discipline/<int:pk>/` | discipline_detail | **Détail de la discipline** | Voir les détails |
| `/eleves/discipline/<int:pk>/modifier/` | discipline_edit | **Modifier la discipline** | Modifier |
| `/eleves/discipline/<int:pk>/supprimer/` | discipline_delete | **Supprimer la discipline** | Supprimer |
| `/eleves/discipline/<int:pk>/traiter/` | discipline_treat | **Traiter la discipline** | Marquer comme traité |
| `/eleves/discipline/statistiques/` | discipline_statistics | **Statistiques discipline** | Graphiques et statistiques |
| `/eleves/discipline/historique/<int:eleve_id>/` | discipline_history | **Historique élève** | Historique disciplinaire d'un élève |
| `/eleves/discipline/export/` | discipline_export | **Exporter disciplines** | Exporter en Excel/PDF |
| `/eleves/discipline/batch/` | discipline_batch_treat | **Traitement par lot** | Traiter plusieurs disciplina |

---

### 5.11 CONDUITE (`/eleves/conduite/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/conduite/config/` | conduite_config_list | **Configuration conduite** | Configurer les notes de conduite |
| `/eleves/conduite/config/<str:niveau>/` | conduite_config_edit | **Modifier config** | Modifier la configuration |

---

### 5.12 PÉRIODES ET CLÔTURES (`/eleves/periodes/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/eleves/periodes/cloture/` | periode_cloture_list | **Clôtures de périodes** | Liste des périodes closes |
| `/eleves/periodes/cloture/<int:classe_id>/` | periode_cloture_edit | **Clôturer une période** | Clôturer une période |
| `/eleves/periodes/cloture/<int:classe_id>/<int:periode>/supprimer/` | periode_cloture_delete | **Ouvrir une période** | Rouvrir une période |
| `/eleves/notes/cloture/` | note_cloture_list | **Clôtures de notes** | Notes closes par professeur |
| `/eleves/notes/cloture/<int:classe_id>/` | note_cloture_edit | **Clôturer les notes** | Clôturer les notes d'une classe |

---

### 5.13 CLASSES (`/academics/classes/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/classes/` | classe_list | **Liste des classes** | Voir toutes les classes |
| `/academics/classes/ajouter/` | classe_create | **Ajouter une classe** | Créer une nouvelle classe |
| `/academics/classes/<int:pk>/modifier/` | classe_edit | **Modifier la classe** | Éditer une classe |
| `/academics/classes/<int:pk>/supprimer/` | classe_delete | **Supprimer la classe** | Supprimer une classe |

---

### 5.14 MATIÈRES (`/academics/matieres/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/matieres/` | matiere_list | **Liste des matières** | Toutes les matières |
| `/academics/matieres/ajouter/` | matiere_create | **Ajouter une matière** | Créer une nouvelle matière |
| `/academics/matieres/<int:pk>/` | matiere_edit | **Modifier la matière** | Éditer une matière |
| `/academics/matieres/<int:pk>/supprimer/` | matiere_delete | **Supprimer la matière** | Supprimer une matière |

---

### 5.15 PROFESSEURS (`/academics/professeurs/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/professeurs/` | professeur_list | **Liste des professeurs** | Tous les professeurs |
| `/academics/professeurs/ajouter/` | professeur_create | **Ajouter un professeur** | Créer un professeur |
| `/academics/professeurs/<int:pk>/modifier/` | professeur_edit | **Modifier le professeur** | Éditer les informations |
| `/academics/professeurs/<int:pk>/supprimer/` | professeur_delete | **Supprimer le professeur** | Supprimer |

---

### 5.16 ATTRIBUTIONS (`/academics/attributions/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/attributions/` | attribution_list | **Liste des attributions** | Enseignements assignés |
| `/academics/attributions/ajouter/` | attribution_create | **Ajouter une attribution** | Assigner un professeur à une classe |
| `/academics/attributions/<int:pk>/modifier/` | attribution_edit | **Modifier l'attribution** | Modifier |
| `/academics/attributions/<int:pk>/supprimer/` | attribution_delete | **Supprimer l'attribution** | Supprimer |

---

### 5.17 MES CLASSES (`/academics/mes-classes/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/mes-classes/` | mes_classes | **Mes classes** | Classes du professeur connecté |

---

### 5.18 ÉVALUATIONS ET NOTES (`/academics/evaluations/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/evaluations/ajouter/` | evaluation_create | **Ajouter une évaluation** | Créer une nouvelle évaluation |
| `/academics/evaluations/<int:pk>/modifier/` | evaluation_edit | **Modifier l'évaluation** | Modifier les notes |
| `/academics/evaluations/<int:pk>/supprimer/` | evaluation_delete | **Supprimer l'évaluation** | Supprimer |
| `/academics/saisie-notes/` | saisie_notes | **Saisie des notes** | Page principale de saisie |
| `/academics/saisie-notes/<int:classe_pk>/` | saisie_notes_classe | **Saisie par classe** | Saisie pour une classe |
| `/academics/saisie-notes/<int:classe_pk>/<int:matiere_pk>/` | saisie_notes_detail | **Saisie détail** | Saisie détaillée |

---

### 5.19 RELEVÉS ET BULLETINS (`/academics/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/feuille-notes/<int:classe_pk>/` | releve_notes | **Relevé de notes** | Tableau des notes par classe |
| `/academics/statistiques/<int:classe_pk>/` | statistiques_classe | **Statistiques** | Statistiques de la classe |
| `/academics/bulletin-classe/<int:classe_pk>/` | bulletin_classe | **Bulletin de classe** | Bulletins de la classe |
| `/academics/bulletin/eleve/<int:eleve_pk>/` | bulletin_eleve | **Bulletin élève** | Bulletin d'un élève |
| `/academics/bulletin/eleve/<int:eleve_pk>/imprimer/` | bulletin_imprimable | **Imprimer bulletin** | Version imprimable PDF |
| `/academics/fiche-notes/<int:classe_pk>/` | classe_fiche_notes | **Fiche de notes** | Fiche synthétique |
| `/academics/historique-notes/` | releve_notes | **Historique des notes** | Historiqueglobal |
| `/academics/historique-notes/<int:classe_pk>/` | releve_notes | **Historique par classe** | Historique d'une classe |

---

### 5.20 FICHES NOTES (`/academics/fiches-notes/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/fiches-notes/` | fiche_notes_list | **Liste des fiches notes** | Toutes les fiches |
| `/academics/fiche-note/eleve/<int:eleve_pk>/` | fiche_note_eleve | **Fiche note élève** | Fiche d'un élève |
| `/academics/fiche-note/eleve/<int:eleve_pk>/<int:cycle_pk>/<int:matiere_pk>/` | fiche_note_detail | **Fiche détaillée** | Fiche avec cycle et matière |

---

### 5.21 EMPLOI DU TEMPS (`/academics/emploi-du-temps/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/emploi-du-temps/` | emploi_du_temps | **Emploi du temps** | Planning hebdomadaire |
| `/academics/emploi-du-temps/reinitialiser/` | emploi_du_temps_reset | **Réinitialiser** | Réinitialiser l'emploi du temps |

---

### 5.22 SALLES (`/academics/salles/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/salles/` | salle_list | **Liste des salles** | Toutes les salles |
| `/academics/salles/ajouter/` | salle_create | **Ajouter une salle** | Créer une salle |
| `/academics/salles/<int:pk>/modifier/` | salle_edit | **Modifier la salle** | Éditer |
| `/academics/salles/<int:pk>/supprimer/` | salle_delete | **Supprimer la salle** | Supprimer |

---

### 5.23 EXAMENS (`/academics/examens/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/examens/` | examen_list | **Liste des examens** | Tous les examens |
| `/academics/examens/ajouter/` | examen_create | **Créer un examen** | Planifier un examen |
| `/academics/examens/<int:pk>/` | examen_edit | **Modifier l'examen** | Éditer |
| `/academics/examens/<int:pk>/detail/` | examen_detail | **Détail de l'examen** | Voir les détails |
| `/academics/examens/<int:pk>/supprimer/` | examen_delete | **Supprimer l'examen** | Supprimer |
| `/academics/examens/<int:pk>/publier/` | examen_publier | **Publier résultats** | Publier les résultats |
| `/academics/examens/<int:pk>/generer-epreuves/` | examen_generate_epreuves | **Générer épreuves** | Crée les copies pour tous les élèves |

---

### 5.24 CONTRAINTES HORAIRES (`/academics/contraintes/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/academics/contraintes/` | contrainte_list | **Liste des contraintes** | Congés, maladies, permissions |
| `/academics/contraintes/ajouter/` | contrainte_create | **Ajouter une contrainte** | Créer une contrainte |
| `/academics/contraintes/<int:pk>/modifier/` | contrainte_edit | **Modifier la contrainte** | Éditer |
| `/academics/contraintes/<int:pk>/supprimer/` | contrainte_delete | **Supprimer la contrainte** | Supprimer |

---

### 5.25 PRÉSENCES (`/presences/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/presences/` | presence_list | **Liste des présences** | Historique des présences |
| `/presences/appel/<int:classe_pk>/` | faire_appel | **Faire l'appel** | Effectuer l'appel pour une classe |
| `/presences/rapport-retards/` | rapport_retards | **Rapport des retards** | Liste des retards |
| `/presences/statistiques/` | statistiques_presence | **Statistiques présences** | Taux de présence |
| `/presences/mes-seances/` | mes_seances | **Mes séances** | Séances du professeur |
| `/presences/seances/<int:seance_id>/demarrer/` | demarrer_seance | **Démarrer la séance** | Commencer une séance |
| `/presences/seances/<int:seance_id>/terminer/` | terminer_seance | **Terminer la séance** | Terminer une séance |
| `/presences/seances/` | liste_seances | **Liste des séances** | Toutes les séances |
| `/presences/attestation/` | attestation_assiduite_form | **Attestation d'assiduité** | Demander une attestation |
| `/presences/attestation/<int:eleve_pk>/pdf/` | attestation_assiduite_pdf | **Télécharger attestation** | Générer PDF |

---

### 5.26 FINANCES - ANNÉES SCOLAIRES (`/finances/annees/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/annees/` | annee_list | **Liste des années scolaires** |Toutes les années |
| `/finances/annees/ajouter/` | annee_create | **Créer une année** | Créer une nouvelle année |
| `/finances/annees/<int:pk>/modifier/` | annee_edit | **Modifier l'année** | Éditer |
| `/finances/annees/<int:pk>/supprimer/` | annee_delete | **Supprimer l'année** | Supprimer |
| `/finances/annees/<int:pk>/activer/` | annee_activer | **Activer l'année** | Définir comme année active |
| `/finances/annees/<int:pk>/selectionner/` | annee_selectionner | **Sélectionner l'année** | Changer d'année scolaire active |

---

### 5.27 FINANCES - FRAIS SCOLAIRES (`/finances/frais/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/frais/` | frais_list | **Liste des frais** | Tous les frais scolaires |
| `/finances/frais/ajouter/` | frais_create | **Ajouter un frais** | Créer un nouveau frais |
| `/finances/frais/<int:pk>/modifier/` | frais_update | **Modifier le frais** | Éditer |

---

### 5.28 FINANCES - PAIEMENTS (`/finances/paiements/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/paiements/` | paiement_list | **Liste des paiements** | Tous les paiements reçus |
| `/finances/paiements/ajouter/` | paiement_create | **Enregistrer un paiement** | Nouveau paiement |
| `/finances/paiements/ajouter/<int:eleve_pk>/` | paiement_create_eleve | **Paiement pour élève** | Paiement pour un élève spécifique |
| `/finances/paiements/<int:paiement_pk>/recu/` | recu_paiement | **Reçu de paiement** | Générer le reçu PDF |

---

### 5.29 FINANCES - COMPTES ÉLÈVES (`/finances/eleve/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/eleve/<int:eleve_pk>/compte/` | etat_compte_eleve | **État du compte** | État de compte d'un élève |
| `/finances/eleve/<int:eleve_pk>/paiements/` | historique_paiements_eleve | **Historique paiements** | Historique des paiement |

---

### 5.30 FINANCES - SALAIRES (`/finances/salaires/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/salaires/` | gestion_salaires | **Gestion des salaires** | Liste des salaires |
| `/finances/salaires/ajouter/` | salaire_create | **Ajouter un salaire** | Enregistrer un salaires |

---

### 5.31 FINANCES - CAISSSE ET CHARGES (`/finances/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/caisse/` | operation_caisse | **Opération de caisse** | Encaissements et décaissements |
| `/finances/charges/` | charges_list | **Liste des charges** | Toutes les charges |
| `/finances/charges/fixe/ajouter/` | charge_fixe_create | **Ajouter charge fixe** | Créer une charge fixe |
| `/finances/charges/fixe/<int:pk>/modifier/` | charge_fixe_edit | **Modifier charge fixe** | Éditer |
| `/finances/charges/fixe/<int:pk>/supprimer/` | charge_fixe_delete | **Supprimer charge fixe** | Supprimer |
| `/finances/charges/operationnelle/ajouter/` | charge_operationnelle_create | **Ajouter charge opérationnelle** | Créer une charge |
| `/finances/charges/operationnelle/<int:pk>/supprimer/` | charge_operationnelle_delete | **Supprimer charge** | Supprimer |

---

### 5.32 FINANCES - PERSONNEL (`/finances/personnel/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/personnel/` | personnel_list | **Liste du personnel** | Tous les membres du personnel |
| `/finances/personnel/ajouter/` | personnel_create | **Ajouter un membre** | Créer un employé |
| `/finances/personnel/<int:pk>/modifier/` | personnel_edit | **Modifier le membre** | Éditer |
| `/finances/personnel/<int:pk>/supprimer/` | personnel_delete | **Supprimer le membre** | Supprimer |

---

### 5.33 FINANCES - TABLEAU DE BORD (`/finances/tableau-bord/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/tableau-bord/` | tableau_bord_financier | **Tableau de bord financier** | Vue d'ensemble financière |

---

### 5.34 FINANCES - RAPPELS (`/finances/rappels/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/rappels/` | liste_rappels | **Liste des rappels** | Rappels de paiement |
| `/finances/generer-rappels/` | generer_rappels | **Générer des rappels** | Créer automatique des rappels |

---

### 5.35 FINANCES - CYCLES (`/finances/cycles/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/cycles/` | cycle_list | **Liste des cycles** | Trimestres/Semestres |
| `/finances/cycles/ajouter/` | cycle_create | **Ajouter un cycle** | Créer un cycle |
| `/finances/cycles/<int:pk>/` | cycle_edit | **Modifier le cycle** | Éditer |
| `/finances/cycles/<int:pk>/supprimer/` | cycle_delete | **Supprimer le cycle** | Supprimer |

---

### 5.36 FINANCES - ÉLÈVES EN RETARD (`/finances/eleves-en-retard/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/eleves-en-retard/` | eleves_en_retard | **Élèves en retard** | Liste des impayés |

---

### 5.37 FINANCES - FACTURES (`/finances/factures/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/factures/` | facture_list | **Liste des factures** | Toutes les factures |
| `/finances/factures/ajouter/` | facture_create | **Créer une facture** | Émettre une facture |
| `/finances/factures/<int:pk>/` | facture_detail | **Détail de la facture** | Voir la facture |
| `/finances/factures/<int:pk>/pdf/` | facture_pdf | **Télécharger PDF** | Générer PDF |

---

### 5.38 FINANCES - BOURSES (`/finances/bourses/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/bourses/` | bourse_list | **Liste des bourses/remises** | Toutes les bourses |
| `/finances/bourses/ajouter/` | bourse_create | **Ajouter une bourse/remise** | Créer une bourse |

---

### 5.39 FINANCES - CATÉGORIES DÉPENSES (`/finances/categories-depense/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/categories-depense/` | categorie_depense | **Catégories de dépenses** | Gestion catégories |

---

### 5.40 FINANCES - RAPPORT FINANCIER (`/finances/rapport-financier/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/finances/rapport-financier/` | rapport_financier | **Rapport financier** | Générer un rapport |

---

### 5.41 RAPPORTS - BULLETINS (`/rapports/bulletins/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/rapports/bulletins/` | bulletin_list | **Liste des bulletins** | Tous les bulletins |
| `/rapports/bulletin/classe/<int:classe_pk>/` | bulletins_par_classe | **Bulletins par classe** | Bulletins d'une classe |
| `/rapports/bulletin/classe/<int:classe_pk>/<int:cycle_pk>/` | bulletins_par_classe_cycle | **Bulletins par cycle** | Bulletins d'un cycle |
| `/rapports/bulletin/generer/<int:inscription_pk>/` | generer_bulletin | **Générer bulletin** | Créer bulletin pour un élève |
| `/rapports/bulletin/pdf/<int:bulletin_pk>/` | exporter_bulletin_pdf | **Télécharger PDF** | Exporter en PDF |

---

### 5.42 RAPPORTS - RAPPORTS (`/rapports/`)

| URL | Nom de la vue | Titre de la page |
|-----|---------------|-----------------|
| `/rapports/academique/` | rapport_academique | **Rapport académique** | Statistiques scolaires |
| `/rapports/financier/` | rapport_financier | **Rapport financier** | Bilan financier |
| `/rapports/transition-annee/` | transition_annee | **Transition d'année** | Passer à une nouvelle année |

---

### 5.43 API REST (`/api/`)

#### Authentification JWT

| URL | Méthode | Description |
|-----|---------|-------------|
| `/api/token/` | POST | Obtenir un token JWT (username, password) |
| `/api/token/refresh/` | POST | Rafraîchir un token expiré |

#### Endpoints disponibles

| URL | ViewSet | Description | Filtres | Actions personnalisées |
|-----|---------|-------------|---------|----------------------|
| `/api/users/` | UserViewSet | Gestion des utilisateurs | role, is_active | - |
| `/api/eleves/` | EleveViewSet | Gestion des élèves | statut, sexe | inscriptions |
| `/api/inscriptions/` | InscriptionViewSet | Inscriptions | annee_scolaire, classe | - |
| `/api/classes/` | ClasseViewSet | Gestion des classes | niveau, annee_scolaire | eleves, matieres |
| `/api/matieres/` | MatiereViewSet | Matières | classe | - |
| `/api/professeurs/` | ProfesseurViewSet | Professeurs | statut | enseignements |
| `/api/enseignements/` | EnseignementViewSet | Enseignements | professeur, classe, annee_scolaire | - |
| `/api/evaluations/` | EvaluationViewSet | Évaluations/Notes | eleve, matiere, type_eval, annee_scolaire | by_classe |
| `/api/annees/` | AnneeScolaireViewSet | Années scolaires | - | active |
| `/api/frais/` | FraisScolaireViewSet | Frais scolaires | classe, annee_scolaire, type_frais | - |
| `/api/paiements/` | PaiementViewSet | Paiements | eleve, frais, mode_paiement | eleve |
| `/api/presences/` | PresenceViewSet | Présences | eleve, classe, statut, justifie | statistiques |
| `/api/salaires/` | SalaireViewSet | Salaires | personnel, annee, statut | - |

#### Sérializers disponibles

| Serializer | Modèle | Champs principaux |
|------------|--------|------------------|
| UserSerializer | User | id, username, email, first_name, last_name, role, telephone, is_active |
| EleveSerializer | Eleve | id, matricule, nom, prenom, date_naissance, lieu_naissance, sexe, adresse, telephone_parent, email_parent, statut |
| InscriptionSerializer | Inscription | id, eleve, eleve_nom, classe, classe_nom, annee_scolaire, date_inscription, moyenne_generale, mention, decision, rang |
| ClasseSerializer | Classe | id, nom, niveau, niveau_display, filiere, annee_scolaire, capacite |
| MatiereSerializer | Matiere | id, nom, coefficient, classe, classe_nom |
| ProfesseurSerializer | Professeur | id, nom, prenom, email, telephone, date_embauche, statut, salaire_base |
| EnseignementSerializer | Enseignement | id, professeur, professeur_nom, classe, classe_nom, matiere, matiere_nom |
| EvaluationSerializer | Evaluation | id, eleve, eleve_nom, matiere, matiere_nom, type_eval, date_eval, note, coefficient, observations |
| AnneeScolaireSerializer | AnneeScolaire | id, libelle, date_debut, date_fin, est_active |
| FraisScolaireSerializer | FraisScolaire | id, classe, annee_scolaire, type_frais, type_display, montant, echeance |
| PaiementSerializer | Paiement | id, eleve, eleve_nom, frais, frais_type, date_paiement, montant, mode_paiement, reference, observations |
| PresenceSerializer | Presence | id, eleve, eleve_nom, classe, date, statut, motif_absence, justifie, observations |
| SalaireSerializer | Salaire | id, personnel, personnel_nom, mois, mois_display, annee, salaire_brut, retenues, salaire_net, date_versement, statut |

---

## 6. MIDDLEWARE

### 6.1 ActiveAnneeMiddleware
- **Fichier** : `core/middleware.py`
- **Objectif** : Définit automatiquement l'année scolaire active pour chaque requête
- **Fonctionnement** :
  - Vérifie d'abord la session de l'utilisateur (`annee_scolaire_id`)
  - Si aucune session, cherche l'année marquée comme active dans la base
  - Rend l'année accessible via `request.annee_active`

### 6.2 SessionTimeoutMiddleware
- **Fichier** : `core/middleware.py`
- **Objectif** : Déconnecte automatiquement après 5 minutes (300 secondes) d'inactivité
- **Fonctionnement** :
  - Enregistre `last_activity` dans la session à chaque requête
  - Vérifie si le temps écoulé dépasse 300 secondes
  - Déconnecte automatiquement et redirige vers la page de connexion

---

## 7. CONTEXT PROCESSORS

### 7.1 annee_scolaire_actuelle
- **Fichier** : `core/context_processors.py`
- **Variables disponibles** :
  - `annee_scolaire` : Année scolaire active
  - `annee` : Alias de annee_scolaire
  - `annees` : Liste de toutes les années scolaires

### 7.2 notification_count
- **Fichier** : `core/context_processors.py`
- **Variables disponibles** :
  - `notification_count` : Nombre de notifications non lues
  - `unread_notifications_count` : Alias (notifications non lues)
  - `unread_messages_count` : Nombre de messages non lus

---

## 8. FLUX DE TRAVAIL TYPIQUE

### 8.1 Inscription d'un nouvel élève

1. **Direction** ou **Secregistrement** crée l'année scolaire (si nouvelle)
2. **Direction** crée les classes pour l'année
3. **Secregistrement** inscrie l'élève via `/eleves/ajouter/`
4. **Secregistrement** ajoute les parents/tuteurs via `/eleves/parents/ajouter/<eleve_id>/`
5. **Secregistrement** effectue l'inscription dans une classe via `/eleves/` → Inscription

### 8.2 Gestion académique

1. **Direction** crée les matières via `/academics/matieres/`
2. **Direction** crée les professors via `/academics/professeurs/`
3. **Direction** attribue les enseignements via `/academics/attributions/`
4. **Professor** saisir les notes via `/academics/saisie-notes/`
5. **Professor** génère les bulletins via `/rapports/bulletin/generer/`

### 8.3 Gestion financière

1. **Direction** définit les frais via `/finances/frais/ajouter/`
2. **Comptable** enregistre les paiements via `/finances/paiements/ajouter/`
3. **Comptable** gère les charges via `/finances/charges/`
4. **Comptable** génère les rapports via `/finances/rapport-financier/`
5. **Comptable** gère les salaires via `/finances/salaires/`

### 8.4 Suivi des présences

1. **Professor** fait l'appel via `/presences/appel/<classe_id>/`
2. **Surveillance** consulte les statistiques via `/presences/statistiques/`
3. **Secregistrement** génère les attestations via `/presences/attestation/`

### 8.5 Discipline

1. **Surveillance** ou **Direction** enregistre une sanction via `/eleves/discipline/ajouter/`
2. Traitement de la discipline via `/eleves/discipline/<id>/traiter/`
3. Notification automatique aux parents

---

## 9. PERMISSIONS PAR RÔLE

| Rôle | Accès principal |
|------|----------------|
| **superadmin** | Accès complet à toutes les fonctionnalités |
| **direction** | Gestion stratégique, approbations, rapports globaux |
| **secretaire** | Inscriptions, gestion quotidienne des élèves |
| **comptable** | Finances, paiements, salaires |
| **professeur** | Notes, évaluations, mes classes |
| **surveillance** | Discipline, présences |

---

## 10. FONCTIONNALITÉS PRINCIPALES PAR MODULE

### 10.1 Accounts
- Authentification avec JWT
- Authentification 2FA (TOTP + codes de secours)
- Gestion des utilisateurs avec quotas
- Permissionsgranulaires par rôle et utilisateur
- Notifications en temps réel
- Messages internes
- Journal d'audit complet
- Verrouillage de compte après échecs
- Demandes d'approbation

### 10.2 Élèves
- Gestion complète du profil élève
- Dossier médical sécurisé
- Gestion des parents/tuteurs
- Inscriptions multiples (par année)
- Sanctions et récompenses avec points
- Configuration de la conduite
- Clôture des périodes et notes
- Documents uploadés

### 10.3 Academics
- Gestion des classes (maternelle → université)
- Matières avec coefficients
- Professeurs avec enseignements
- Évaluations et examens
- Saisie de notes enrichie
-生成 de bulletins
- Gestion des emploi du temps
- Contraintes horaires (congés, maladies)

### 10.4 Presences
- Appel quotidien
- Suivi des retards et absences
- Justification des absences
- Séances de cours
- Attestations d'assiduité

### 10.5 Finances
- Années scolaires et cycles
- Frais scolaires flexibles (par classe/niveau)
- Paiements avec reçus
- Gestion du personnel et salaires
- Charges fixes et opérationnelles
- Facturation
- Bourses et remises
- Rapports financiers détaillés
- Génération automatique des rappels

### 10.6 Rapports
- Bulletins individuels et par classe
- Statistiques académiques
- Rapports financiers
- Transition d'année scolaire

---

## 11. TECHNOLOGIES UTILISÉES

### 11.1 Backend
- **Python** 3.x
- **Django** 4.x
- **Django REST Framework**
- **PyJWT** (Authentification)
- **PyOTP** (2FA)
- **django-filter**
- **corsheaders**

### 11.2 Base de données
- **SQLite3** (défaut)
- **PostgreSQL** (production)
- **MySQL** (production)

### 11.3 Frontend
- **HTML5**
- **CSS3** (Bootstrap/Custom)
- **JavaScript** (jQuery)
- **Chart.js** (Graphiques)

### 11.4 Outils
- **Git** (Versioning)
- **virtualenv** (Environnement virtuel)

---

## 12. INSTALLATION ET DÉMARRAGE

### 12.1 Prérequis
- Python 3.8+
- pip

### 12.2 Installation

```bash
# Activer l'environnement virtuel
cd gestion_ecole
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### 12.3 Accès

- **Local** : http://127.0.0.1:8000
- **Admin Django** : http://127.0.0.1:8000/admin/

---

## 13. STRUCTURE DES DOSSIERS

```
gestion_ecole/
├── accounts/              # Gestion utilisateurs
├── academics/            # Gestion académique
├── eleves/               # Gestion élèves
├── finances/             # Gestion financière
├── presences/            # Suivi présences
├── rapports/            # Génération rapports
├── core/                # Configuration centrale
├── templates/           # Templates HTML
├── static/              # Fichiers statiques
├── media/               # Fichiers uploadés
├── scripts/             # Scripts de déploiement
└── venv/               # Environnement virtuel
```

---

## 14. NOTES IMPORTANTES

- Tous les montants sont en **FCFA** (Franc CFA)
- La langue par défaut est le **français**
- Le fuseau horaire est **Africa/Douala** (UTC+1)
- L'authentification 2FA utilise **TOTP** (Google Authenticator compatible)
- Le système gère les **approbations** pour certaines actions sensibles

---

*Document généré automatiquement - Dernière mise à jour : 2026*