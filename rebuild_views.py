"""Script pour reconstruire correctement les fichiers de vues"""
import re

def rebuild_views_file(filepath):
    """Reconstruire un fichier de vues corrompu"""
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher et corriger les problèmes:
    # 1. Lignes @login_required/@user_passes_test dupliqués
    # 2. Lignes de code mal indentées après décorateurs
    # 3. Lignes vides excessives
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    in_function = False
    func_indent = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Ignorer les lignes vides multiples
        if stripped == '':
            if new_lines and new_lines[-1].strip() != '':
                new_lines.append('')
            i += 1
            continue
        
        # Si c'est un décorateur
        if stripped in ['@login_required', '@user_passes_test']:
            # Ne pas ajouter de doublons
            if new_lines and new_lines[-1].strip() in ['@login_required', '@user_passes_test']:
                i += 1
                continue
            new_lines.append(line)
            i += 1
            continue
        
        # Si c'est une définition de fonction
        if stripped.startswith('def '):
            new_lines.append(line)
            in_function = True
            i += 1
            continue
        
        # Si on est dans une fonction et la ligne est du code
        if in_function:
            # Calculer l'indentation
            indent = len(line) - len(line.lstrip())
            
            # Si c'est une ligne de vérification de permission
            if stripped.startswith('if not request.user.has_module_permission'):
                # Ajouter avec l'indentation correcte (4 espaces)
                if not line.startswith('    '):
                    new_lines.append('    ' + stripped)
                else:
                    new_lines.append(line)
                i += 1
                continue
            
            # Si c'est messages.error ou return redirect
            if stripped.startswith('messages.error') or stripped.startswith('return redirect'):
                # Ajouter avec l'indentation correcte (8 espaces)
                if not line.startswith('        '):
                    new_lines.append('        ' + stripped)
                else:
                    new_lines.append(line)
                i += 1
                continue
            
            # Si c'est du code normal, ajouter avec l'indentation de la fonction
            if stripped.startswith('if ') or stripped.startswith('for ') or stripped.startswith('while '):
                new_lines.append(line)
                i += 1
                continue
            
            if stripped.startswith('return ') and 'redirect' not in stripped and 'render' not in stripped:
                new_lines.append(line)
                i += 1
                continue
            
            if stripped.startswith('from ') or stripped.startswith('import '):
                new_lines.append(line)
                i += 1
                continue
            
            # Autres lignes de code - ajouter directement
            if indent > 0:
                new_lines.append(line)
                i += 1
                continue
        
        # Lignes en dehors des fonctions - vérifier si c'est du code orphelin
        if stripped.startswith('    '):
            # Code orphelin, probablement une erreur - ignorer
            i += 1
            continue
        
        if stripped.startswith('        '):
            # Code profondément orphelin - ignorer
            i += 1
            continue
        
        # Autres cas - ajouter tel quel
        new_lines.append(line)
        i += 1
    
    # Supprimer les lignes vides au début et à la fin
    while new_lines and new_lines[0].strip() == '':
        new_lines.pop(0)
    while new_lines and new_lines[-1].strip() == '':
        new_lines.pop()
    
    # Supprimer les lignes vides multiples
    result = []
    prev_empty = False
    for line in new_lines:
        if line.strip() == '':
            if not prev_empty:
                result.append(line)
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False
    
    content_fixed = '\n'.join(result)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print(f"  Fichier reconstruit")

# Reconstruire les fichiers
rebuild_views_file('authentification/views.py')
rebuild_views_file('finances/views.py')
rebuild_views_file('rapports/views.py')
rebuild_views_file('scolarite/views.py')
rebuild_views_file('enseignement/views.py')

print("\nTerminé!")
