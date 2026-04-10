"""Script de reconstruction complète pour finances/views.py"""
import re

def reconstruct_finances():
    # Lire le fichier corrompu
    with open('finances/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Étapes de nettoyage:
    # 1. Corriger les lignes fusionnées (deux lignes sur une)
    # 2. Supprimer les fonctions en double
    # 3. Corriger les indentations manquantes
    
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Étape 1: Corriger les lignes fusionnées
        # Pattern: "messages.error(...)        return redirect(...)"
        if re.search(r'messages\.error.*\w+.*return redirect', stripped):
            # Séparer en deux lignes
            parts = re.split(r'(\s*return redirect)', stripped)
            for part in parts:
                if part.strip():
                    new_lines.append(part)
            i += 1
            continue
        
        # Étape 2: Si c'est une ligne vide excessive, l'ignorer
        if not stripped:
            # Ne pas ajouter plus de 2 lignes vides consécutives
            if not new_lines or new_lines[-1].strip() != '':
                new_lines.append('')
            elif len(new_lines) >= 2 and new_lines[-1] == '' and new_lines[-2] == '':
                pass  # Ignorer cette ligne vide
            else:
                new_lines.append('')
            i += 1
            continue
        
        # Étape 3: Supprimer les décorateurs @user_passes_test
        if stripped == '@user_passes_test':
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    
    # Étape 4: Supprimer les définitions de fonctions dupliquées
    lines = content.split('\n')
    seen_funcs = set()
    new_lines = []
    
    for line in lines:
        match = re.match(r'(@\w+)\s*$', line.strip())
        if line.strip().startswith('@login_required'):
            # Garder un seul @login_required
            if '@login_required' not in seen_funcs:
                seen_funcs.add('@login_required')
                new_lines.append(line)
            continue
        
        # Garder les lignes qui ne sont pas des décorateurs dupliqués
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Écrire le fichier
    with open('finances/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fichier reconstruit")

reconstruct_finances()
