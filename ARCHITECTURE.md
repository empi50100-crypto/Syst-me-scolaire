# SYSTÈME DE GESTION SCOLAIRE - DOCUMENTATION ARCHITECTURALE (V2)

## 1. PRÉSENTATION DU PROJET

SyGeS-AM est un système de gestion d'établissement scolaire robuste, conçu pour centraliser toutes les activités administratives, académiques et financières.

### 1.1 Caractéristiques techniques
- **Framework** : Django 5.x (Python 3.11+)
- **Base de données** : PostgreSQL (Recommandé pour la production)
- **API REST** : Django REST Framework (JWT Authentication)
- **Sécurité** : Authentification à deux facteurs (2FA), Journal d'audit complet
- **Langue** : 100% Français (Modèles, URLs, Interface)

---

## 2. RÔLES D'UTILISATEURS

| Rôle | Description |
|------|-------------|
| `superadmin` | Administrateur total du système. |
| `direction` | Pilotage stratégique et approbations. |
| `secretaire` | Inscriptions, gestion des classes et des documents. |
| `comptable` | Finances, salaires et opérations de caisse. |
| `professeur` | Saisie des notes, appels et suivi pédagogique. |
| `surveillance` | Discipline, présences et ponctualité. |

---

## 3. ARCHITECTURE DES SERVICES (8 APPLICATIONS)

| Application | Responsabilité | Modèles Clés |
|-------------|----------------|--------------|
| **authentification** | Identité et accès | `Utilisateur`, `ProfilPermission`, `JournalAudit`, `Notification`, `Message` |
| **core** | Paramétrage central | `AnneeScolaire`, `Cycle`, `NiveauScolaire`, `PeriodeEvaluation` |
| **scolarite** | Suivi des élèves | `Eleve`, `EleveInscription`, `SanctionRecompense`, `DossierMedical`, `DocumentEleve` |
| **enseignement** | Pédagogie | `Classe`, `Matiere`, `ProfilProfesseur`, `Attribution`, `Examen`, `Evaluation` |
| **presences** | Ponctualité | `Presence`, `Appel`, `SeanceCours` |
| **finances** | Gestion monétaire | `FraisScolaire`, `Paiement`, `OperationCaisse`, `ChargeFixe`, `Facture` |
| **ressources_humaines** | Personnel | `MembrePersonnel`, `Salaire`, `ContratEmploye`, `Conge` |
| **rapports** | Documents & Stats | `Bulletin` |

---

## 4. MODÈLES DE DONNÉES DÉTAILLÉS

### 4.1 Authentification
- **Utilisateur** : Modèle étendu d'AbstractUser avec rôles, téléphone, 2FA et profils de permissions.
- **JournalAudit** : Trace chaque création, modification et suppression avec l'utilisateur et l'IP.
- **ProfilPermission** : Groupe de modules autorisés pour un ensemble d'utilisateurs.

### 4.2 Core
- **AnneeScolaire** : Gère les dates de début/fin et l'état "active".
- **NiveauScolaire** : Définit les niveaux (ex: CP1, 6ème, L1) rattachés à un **Cycle**.
- **PeriodeEvaluation** : Trimestres ou Semestres rattachés à une année.

### 4.3 Scolarité
- **Eleve** : Fiche centrale (Matricule `ELV...`).
- **EleveInscription** : Lien historique entre un élève, une classe et une année scolaire.
- **SanctionRecompense** : Suivi disciplinaire et valorisation des élèves.
- **ConfigurationConduite** : Paramétrage de la note de conduite de base.

### 4.4 Enseignement
- **Classe** : Entité pédagogique (ex: 6ème A) liée à une année et un niveau.
- **ProfilProfesseur** : Extension de l'utilisateur pour les enseignants (spécialité, statut).
- **Attribution** : Assignation d'un professeur à une matière dans une classe.
- **Evaluation** : Notes individuelles saisies par les professeurs.
- **Examen** : Épreuves programmées (Devoirs, Compositions).

### 4.5 Finances
- **FraisScolaire** : Montants dus par classe ou niveau (Scolarité, Inscription, Cantine).
- **Paiement** : Encaissements liés aux frais avec mode de règlement.
- **OperationCaisse** : Suivi des flux de trésorerie (Encaissement/Décaissement).
- **ChargeFixe** : Dépenses récurrentes (Loyer, Électricité).

### 4.6 Ressources Humaines
- **MembrePersonnel** : Informations administratives de tous les employés.
- **Salaire** : Suivi mensuel des versements et retenues.
- **ContratEmploye** : Type de contrat, dates et conditions.

---

## 5. FLUX DE DONNÉES PRINCIPAUX

1. **Cycle Académique** : `Core` (Année) → `Enseignement` (Classes/Matières) → `Scolarité` (Inscriptions).
2. **Cycle de Notation** : `Enseignement` (Examens) → `Evaluation` (Saisie) → `Rapports` (Bulletins).
3. **Cycle Financier** : `Finances` (Frais) → `Finances` (Paiements) → `Finances` (Caisse).

---

*Documentation mise à jour : Avril 2026*
*Version Architecture : 2.0*
