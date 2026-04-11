"""Corriger les problèmes d'indentation dans enseignement/views.py"""
import re

with open('enseignement/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Corriger les return redirect mal indentés (devrait avoir l'indentation du bloc parent)
    if stripped.startswith('return redirect('):
        # Ajouter 4 espaces pour être dans le bloc if/else
        if not line.startswith('        ') and not line.startswith('            '):
            # Deviner l'indentation basée sur le contexte
            if new_lines and new_lines[-1].strip().startswith(('if ', 'else:', 'messages.success')):
                new_lines.append('            ' + stripped)
                i += 1
                continue
    
    # Supprimer les else: orphelins (sans if correspondant)
    if stripped == 'else:':
        # Vérifier si le else correspond à un if dans les lignes précédentes
        # Chercher un if dans les 10 lignes précédentes
        has_matching_if = False
        for j in range(max(0, len(new_lines) - 20), len(new_lines)):
            if new_lines[j].strip().startswith(('if ', 'elif ')):
                has_matching_if = True
                break
        
        if not has_matching_if:
            # C'est un else orphelin - ajouter un # pour le commenter ou l'ignorer
            # Ou simplement supprimer la ligne
            i += 1
            continue
    
    new_lines.append(line)
    i += 1

content = '\n'.join(new_lines)

with open('enseignement/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Corrigé")
