#!/usr/bin/env python3
"""
Test de vérification que l'import circulaire est résolu
"""

import sys

print("🔍 Test de vérification de l'import")
print("=" * 50)

# Test 1: Importer le module corrigé
try:
    from tools.action_plan_form import ActionPlanForm
    print("✅ Test 1 PASSE: Import de ActionPlanForm réussi")
except Exception as e:
    print(f"❌ Test 1 ÉCHEC: {e}")
    sys.exit(1)

# Test 2: Créer une instance
try:
    form = ActionPlanForm(
        title="Mon Plan d'Action",
        priority="high",
        created_by="test_user"
    )
    print(f"✅ Test 2 PASSE: Instance créée - {form}")
except Exception as e:
    print(f"❌ Test 2 ÉCHEC: {e}")
    sys.exit(1)

# Test 3: Ajouter une tâche
try:
    form.add_task("Première tâche", "Description de la tâche")
    form.add_task("Deuxième tâche")
    print(f"✅ Test 3 PASSE: Tâches ajoutées - {len(form.tasks)} tâches")
except Exception as e:
    print(f"❌ Test 3 ÉCHEC: {e}")
    sys.exit(1)

# Test 4: Convertir en dict
try:
    data = form.to_dict()
    print(f"✅ Test 4 PASSE: Conversion en dict réussie")
    print(f"   Titre: {data['title']}")
    print(f"   Priorité: {data['priority']}")
    print(f"   Nombre de tâches: {len(data['tasks'])}")
except Exception as e:
    print(f"❌ Test 4 ÉCHEC: {e}")
    sys.exit(1)

# Test 5: Changer le statut
try:
    form.update_status("active")
    print(f"✅ Test 5 PASSE: Statut changé en '{form.status}'")
except Exception as e:
    print(f"❌ Test 5 ÉCHEC: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("🎉 TOUS LES TESTS ONT RÉUSSI!")
print("\nL'import circulaire est maintenant résolu.")
print("Le fichier utilise l'approche TYPE HINT uniquement.")
print("=" * 50)
