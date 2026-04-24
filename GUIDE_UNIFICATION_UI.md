# 🎨 GUIDE D'UNIFICATION UI - SYGES-AM

## Version: 2026.04.23

---

## ✅ TEMPLATES DÉJÀ UNIFIÉS

### Pages de Liste (List Views)
1. ✅ `scolarite/eleve_list.html`
2. ✅ `scolarite/discipline_list.html`
3. ✅ `enseignement/professeur_list.html`
4. ✅ `finances/paiement_list.html`
5. ✅ `authentification/user_list.html`
6. ✅ `enseignement/classe_list.html`
7. ✅ `enseignement/matiere_list.html`

### Formulaires
1. ✅ `scolarite/eleve_form.html`

---

## 📦 COMPOSANTS RÉUTILISABLES

### 1. Page Header (En-tête de page)
**Fichier:** `templates/includes/page_header.html`

**Usage:**
```html
{% url 'app:model_create' as create_url %}
{% include 'includes/page_header.html' with 
    title="Liste des éléments" 
    icon="bi-collection" 
    show_button=True 
    button_url=create_url 
    button_text="Nouveau" 
    button_icon="bi-plus-circle" 
%}
```

**Résultat:**
- Titre avec icône à gauche
- Bouton "Nouveau" stylisé avec dégradé à droite
- Bordure inférieure subtile

---

### 2. Filters Card (Carte de filtres)
**Classe CSS:** `filters-card`

**Usage:**
```html
<div class="card filters-card mb-4">
    <div class="card-header">
        <h5><i class="bi bi-funnel"></i> Filtres et Recherche</h5>
    </div>
    <div class="card-body">
        <form method="get" class="row g-3 align-items-end">
            <!-- Champs de filtre -->
            <div class="col-md-3">
                <label class="form-label">Nom</label>
                <input type="text" name="search" class="form-control" placeholder="Rechercher...">
            </div>
            <div class="col-12 d-flex justify-content-end gap-2 mt-3">
                <a href="{% url 'app:model_list' %}" class="btn btn-secondary">
                    <i class="bi bi-arrow-counterclockwise"></i> Réinitialiser
                </a>
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-funnel"></i> Filtrer
                </button>
            </div>
        </form>
    </div>
</div>
```

**Résultat:**
- Header dégradé indigo/violet
- Labels en uppercase
- Boutons alignés à droite

---

### 3. Table Container (Conteneur de tableau)
**Classe CSS:** `table-container`

**Usage:**
```html
<div class="table-container">
    <div class="table-responsive">
        <table class="table table-hover mb-0" id="tableId">
            <thead>
                <tr>
                    <th><i class="bi bi-person me-1"></i>Nom</th>
                    <th><i class="bi bi-envelope me-1"></i>Email</th>
                    <th style="width: 120px;" class="text-center"><i class="bi bi-gear me-1"></i>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td>{{ item.nom }}</td>
                    <td>{{ item.email }}</td>
                    <td class="text-center">
                        <!-- Boutons d'action -->
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="3" class="p-0">
                        <!-- Empty state -->
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

**Résultat:**
- Header sombre dégradé
- Icônes dans les en-têtes
- Hover sur les lignes
- Ombre portée

---

### 4. Action Buttons (Boutons d'action)
**Classe CSS:** `action-btns` + classes spécifiques

**Usage:**
```html
<div class="action-btns">
    <a href="{{ view_url }}" class="btn btn-view" title="Voir">
        <i class="bi bi-eye"></i>
    </a>
    <a href="{{ edit_url }}" class="btn btn-edit" title="Modifier">
        <i class="bi bi-pencil"></i>
    </a>
    <a href="{{ delete_url }}" class="btn btn-delete btn-confirm-delete" 
       title="Supprimer" 
       data-confirm-message="Êtes-vous sûr de vouloir supprimer cet élément ?">
        <i class="bi bi-trash"></i>
    </a>
</div>
```

**Styles disponibles:**
- `btn-view` - Bleu (info)
- `btn-edit` - Orange (warning)
- `btn-delete` - Rouge (danger)

**Résultat:**
- Boutons 32x32px carrés arrondis
- Icônes centrées
- Couleurs pastel avec bordures
- Hover avec effet d'élévation

---

### 5. Empty State (État vide)
**Fichier:** `templates/includes/empty_state.html`

**Usage:**
```html
{% include 'includes/empty_state.html' with 
    icon="bi-inbox" 
    title="Aucun élément" 
    message="Commencez par ajouter un élément" 
    button_url=create_url 
    button_text="Ajouter" 
%}
```

**Résultat:**
- Grande icône dans cercle dégradé
- Titre en gras
- Message descriptif
- Bouton d'action

---

### 6. Badges (Badges unifiés)
**Classes CSS:** `badge-*`

**Usage:**
```html
<span class="badge badge-success">Actif</span>
<span class="badge badge-danger">Inactif</span>
<span class="badge badge-warning">En attente</span>
<span class="badge badge-info">Info</span>
<span class="badge badge-primary">Principal</span>
<span class="badge badge-secondary">Secondaire</span>
```

**Résultat:**
- Bordure fine de la même couleur
- Fond clair pastel
- Texte en couleur foncée
- Arrondis 12px

---

### 7. Stat Cards (Cartes de statistiques)
**Classes CSS:** `stat-card stat-card-*`

**Usage:**
```html
<div class="row mb-4 g-3">
    <div class="col-md-3">
        <div class="card stat-card stat-card-primary">
            <div class="card-body">
                <div class="stat-icon"><i class="bi bi-people"></i></div>
                <div class="stat-content">
                    <h6>Total</h6>
                    <h2>{{ count }}</h2>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Variantes disponibles:**
- `stat-card-primary` - Indigo
- `stat-card-success` - Vert
- `stat-card-warning` - Orange
- `stat-card-danger` - Rouge
- `stat-card-info` - Bleu
- `stat-card-secondary` - Gris

---

## 🔄 TEMPLATES RESTANTS À UNIFIER

### Liste des templates à mettre à jour:
- [ ] `authentification/audit_log.html`
- [ ] `authentification/user_form.html`
- [ ] `core/cycle_list.html`
- [ ] `core/niveau_list.html`
- [ ] `core/periode_list.html`
- [ ] `enseignement/attribution_list.html`
- [ ] `enseignement/coefficient_list.html`
- [ ] `enseignement/contrainte_list.html`
- [ ] `enseignement/evaluation_list.html`
- [ ] `enseignement/examen_list.html`
- [ ] `enseignement/salle_list.html`
- [ ] `finances/annee_list.html`
- [ ] `finances/frais_list.html`
- [ ] `finances/facture_list.html`
- [ ] `finances/personnel_list.html`
- [ ] `finances/salaire_list.html`
- [ ] `presences/presence_list.html`
- [ ] `ressources_humaines/personnel_list.html`
- [ ] `scolarite/parent_list.html`
- [ ] `scolarite/inscription_list.html`

### Formulaires à mettre à jour:
- [ ] `enseignement/professeur_form.html`
- [ ] `enseignement/matiere_form.html`
- [ ] `enseignement/classe_form.html`
- [ ] `finances/paiement_form.html`
- [ ] `finances/frais_form.html`
- [ ] `authentification/user_form.html`

---

## 🎨 PALETTE DE COULEURS

### Couleurs Primaires
- `--primary-500` : #6366f1 (Indigo)
- `--primary-600` : #4f46e5 (Indigo foncé)

### Couleurs Fonctionnelles
- `--success` : #10b981 (Vert)
- `--info` : #0ea5e9 (Bleu)
- `--warning` : #f59e0b (Orange)
- `--danger` : #ef4444 (Rouge)

### Neutres
- `--gray-50` à `--gray-900` : Échelle de gris

---

## 📝 CHECKLIST DE MISE À JOUR

Pour chaque template:

- [ ] Remplacer l'en-tête par `page_header.html`
- [ ] Remplacer les filtres par `filters-card`
- [ ] Remplacer le tableau par `table-container`
- [ ] Remplacer les boutons d'action par `action-btns`
- [ ] Remplacer les badges par `badge-*`
- [ ] Remplacer l'état vide par `empty_state.html`
- [ ] Tester en mode sombre
- [ ] Vérifier la réactivité sur mobile

---

## 🚀 COMMANDE RAPIDE

### Mettre à jour tous les templates (script Python):
```python
# Liste des templates à traiter
templates = [
    'core/cycle_list.html',
    'core/niveau_list.html',
    'enseignement/attribution_list.html',
    # ... etc
]

# Pour chaque template:
# 1. Lire le fichier
# 2. Appliquer les transformations
# 3. Sauvegarder
```

---

## 💡 ASTUCES

1. **Sauvegarder avant modification** - Toujours garder une copie du template original
2. **Tester progressivement** - Ne pas tout changer d'un coup
3. **Vérifier les permissions** - Utiliser `{% can_add %}`, `{% can_change %}`, etc.
4. **Conserver la logique métier** - Ne pas supprimer les conditions Django

---

**Dernière mise à jour:** 23 Avril 2026
