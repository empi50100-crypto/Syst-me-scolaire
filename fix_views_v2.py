"""Script pour corriger les fichiers de vues de manière plus précise"""
import re

def fix_view_file(filepath):
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher le pattern problématique:
    # @login_required (avec ou sans doublon)
    # @user_passes_test
    #     if not request.user.has_module_permission
    # ou
    # @login_required
    # def frais_update(request, pk):
    # def NEW_FUNC(request):
    
    # Pattern: décorateur(s) suivi(s) directement par du code sans def
    # Ou définitions de fonctions consécutives sans corps
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Chercher une ligne qui EST une définition de fonction
        if stripped.startswith('def ') and not stripped.startswith('def ') == False:
            # Vérifier si la ligne précédente était aussi une définition de fonction
            if new_lines and new_lines[-1].strip().startswith('def '):
                # Deux définitions consécutives - garder seulement la première (qui est malformée)
                # ou la seconde selon le contexte
                pass
            
            new_lines.append(line)
            i += 1
            continue
        
        # Chercher un @decorator suivi d'une ligne qui n'est pas un @decorator ni un def
        if stripped in ['@login_required', '@user_passes_test']:
            # Regarder les lignes suivantes
            next_lines = []
            j = i + 1
            while j < len(lines) and lines[j].strip() in ['@login_required', '@user_passes_test', '']:
                next_lines.append(lines[j])
                j += 1
            
            # Si après les @decorators on a du code (pas un def), c'est un problème
            if j < len(lines):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('def '):
                    # C'est le cas problématique - manque le def
                    # Chercher le module dans le code
                    func_name = 'view_func'
                    for k in range(j, min(j + 5, len(lines))):
                        check = lines[k].strip()
                        match = re.search(r'has_module_permission\([\'"](\w+)[\'"]', check)
                        if match:
                            func_name = match.group(1) + '_view'
                            break
                        match = re.search(r'render\(request,\s*[\'"](\w+/)?(\w+)_list', check)
                        if match:
                            func_name = match.group(2) + '_list'
                            break
                    
                    # Ajouter le décorateur et la définition
                    new_lines.append(stripped)
                    new_lines.append(f'def {func_name}(request):')
                    i = j  # Continuer à partir du code
                    continue
                elif next_line.startswith('def '):
                    # Deux définitions consécutives - supprimer la première
                    # Ajouter seulement le décorateur
                    new_lines.append(stripped)
                    i += 1
                    continue
        
        new_lines.append(line)
        i += 1
    
    content_fixed = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print(f"  Fichier traité")

# Corriger tous les fichiers
fix_view_file('eleves/views.py')
fix_view_file('finances/views.py')
fix_view_file('rapports/views.py')
fix_view_file('academics/views.py')

print("\nTerminé!")
