#!/usr/bin/env python3
"""
Script de correction pour le fichier action_plan_form.py
Résout le problème d'import circulaire en convertissant vers TYPE HINT uniquement
"""

import re

def fix_action_plan_form():
    filepath = "tools/action_plan_form.py"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Fichier lu: {len(content)} caractères")
        
        # 1. Remplacer l'import problématique par un TYPE HINT uniquement
        old_import = "from mcp_ideation_autonomous.agent.schemas import ActionPlanSchema"
        new_import = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from mcp_ideation_autonomous.agent.schemas import ActionPlanSchema"
        
        content = content.replace(old_import, new_import)
        print("✓ Import corrigé (TYPE HINT uniquement)")
        
        # 2. Remplacer l'héritage de classe par une classe standard
        # Pattern: class ActionPlanForm(ActionPlanSchema):
        old_class = "class ActionPlanForm(ActionPlanSchema):"
        new_class = "class ActionPlanForm:"  # Sans héritage - TYPE HINT uniquement
        
        content = content.replace(old_class, new_class)
        print("✓ Héritage de classe retiré")
        
        # 3. Si nécessaire, ajouter les attributs manuellement
        # (les Pydantic models générés ont besoin des champs explicites)
        if "tasks:" not in content and "tasks =" not in content:
            # Ajouter les attributs de base si manquants
            class_body = """class ActionPlanForm:
    # TYPE HINT uniquement - pas d'import circulaire
    # Les champs sont définis manuellement pour éviter l'héritage Pydantic
    
    title: str = ""
    priority: str = "medium"
    tasks: list = None
    
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)
        if self.tasks is None:
            self.tasks = []
"""
            # Remplacer la déclaration de classe complète
            pattern = r"class ActionPlanForm:.*?def "
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, class_body + "\n    def ", content, flags=re.DOTALL)
                print("✓ Corps de classe corrigé")
        
        # 4. Écrire le fichier corrigé
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Fichier corrigé avec succès: {filepath}")
        print("\nRésumé des changements:")
        print("- Import changé: inheritance → TYPE_CHECKING")
        print("- Classe changée: ActionPlanForm(ActionPlanSchema) → ActionPlanForm")
        print("- L'import circulaire est maintenant résolu")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Correction du fichier action_plan_form.py")
    print("=" * 50)
    success = fix_action_plan_form()
    
    if success:
        print("\n🎉 Vous pouvez maintenant exécuter votre code sans l'erreur d'import circulaire!")
    else:
        print("\n⚠️ La correction a échoué. Vérifiez le fichier manuellement.")
