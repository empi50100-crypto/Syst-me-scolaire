"""Script de reconstruction complète du fichier finances/views.py"""
import re

def reconstruct():
    # Lire le fichier
    with open('finances/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Étape 1: Rejoindre les lignes séparées comme:
        # "        return redirect"
        # "    ('dashboard')"
        if stripped.startswith('return redirect') or stripped.startswith('return redirect,'):
            # Rejoindre avec la ligne suivante si c'est une parenthèse
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('('):
                    combined = stripped + next_line
                    new_lines.append(combined)
                    i += 2
                    continue
        
        # Étape 2: Corriger les lignes messages.error/return redirect mal indentées
        if stripped.startswith('messages.error') or stripped.startswith('return redirect'):
            # Si l'indentation est 4 espaces au lieu de 8
            if line.startswith('    ') and not line.startswith('        '):
                # Ajouter 4 espaces supplémentaires
                new_lines.append('        ' + stripped)
                i += 1
                continue
        
        # Étape 3: Supprimer les lignes @user_passes_test残留
        if stripped == '@user_passes_test':
            i += 1
            continue
        
        # Étape 4: Corriger les lignes @login_required consécutives
        if stripped == '@login_required':
            if new_lines and new_lines[-1].strip() == '@login_required':
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    
    # Étape 5: Supprimer les fonctions en double
    # Trouver toutes les définitions de fonctions
    func_pattern = r'(@login_required\s+)?def (\w+)\(([^)]*)\):'
    matches = list(re.finditer(func_pattern, content))
    
    # Garder seulement la première occurrence de chaque fonction
    seen_funcs = {}
    parts = []
    last_end = 0
    
    for match in matches:
        func_name = match.group(2)
        start = match.start()
        end = match.end()
        
        if func_name not in seen_funcs:
            seen_funcs[func_name] = (start, end)
        else:
            # C'est un doublon - trouver où cette fonction se termine
            # et supprimer son contenu
            prev_start, _ = seen_funcs[func_name]
            # Trouver la fin de cette fonction (prochain @login_required ou def)
            next_match = re.search(r'\n(@login_required\s+\n)', content[end:])
            if next_match:
                dup_end = end + next_match.start()
            else:
                dup_end = len(content)
            
            # Supprimer le doublon
            content = content[:start] + content[dup_end:]
            # Recommencer la recherche
            return reconstruct()
    
    with open('finances/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fichier reconstruit")

reconstruct()
