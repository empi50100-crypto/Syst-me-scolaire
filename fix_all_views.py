"""Script pour corriger tous les fichiers de vues"""
import re

def fix_view_file(filepath):
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    pending_decorators = []
    
    # Mappage des modules vers les noms de fonctions les plus probables
    func_name_from_module = {
        'eleve_list': 'eleve_list',
        'discipline': 'discipline_list',
        'annee_scolaire': 'annee_list',
        'rapport_academique': 'rapport_academique',
        'user_list': 'user_list',
        'saisie_notes': 'saisie_notes',
        'presence_list': 'presence_list',
        'bulletins': 'bulletin_list',
        'fiche_notes': 'fiche_notes',
        'mes_classes': 'mes_classes',
    }
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Si c'est un décorateur
        if stripped in ['@login_required', '@user_passes_test']:
            # Ne pas ajouter de doublons
            if not pending_decorators or pending_decorators[-1] != stripped:
                pending_decorators.append(line)
            i += 1
            continue
        
        # Si on a des décorateurs en attente et on rencontre du code
        if pending_decorators and stripped:
            # Deviner le nom de la fonction
            func_name = 'view_func'
            
            # Chercher des indices dans le code qui suit
            for j in range(i, min(i + 10, len(lines))):
                check_line = lines[j].strip()
                
                # Chercher le module dans has_module_permission
                match = re.search(r'has_module_permission\([\'"](\w+)[\'"]\s*,\s*[\'"](\w+)[\'"]', check_line)
                if match:
                    module_code = match.group(1)
                    func_name = func_name_from_module.get(module_code, f'{module_code}_view')
                    break
                
                # Chercher dans render
                match = re.search(r'render\(request,\s*[\'"](\w+/[\w_]+\.html)[\'"]', check_line)
                if match:
                    template = match.group(1)
                    if 'eleve' in template:
                        func_name = 'eleve_list'
                    elif 'discipline' in template:
                        func_name = 'discipline_list'
                    elif 'classe' in template:
                        func_name = 'classe_list'
                    elif 'user' in template:
                        func_name = 'user_list'
                    break
                
                # Chercher dans redirect
                match = re.search(r'redirect\([\'"](\w+):(\w+)[\'"]', check_line)
                if match:
                    func_name = match.group(2)
                    break
            
            # Ajouter les décorateurs (sans doublons)
            for dec in pending_decorators:
                new_lines.append(dec)
            
            # Ajouter la définition de fonction
            new_lines.append(f'def {func_name}(request):')
            
            pending_decorators = []
            continue
        
        new_lines.append(line)
        i += 1
    
    content_fixed = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print(f"  Fichier traité")

# Corriger tous les fichiers
fix_view_file('scolarite/views.py')
fix_view_file('finances/views.py')
fix_view_file('rapports/views.py')
fix_view_file('enseignement/views.py')

print("\nTerminé!")
