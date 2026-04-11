"""Corriger systématiquement enseignement/views.py"""
import re

with open('enseignement/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Corriger les messages.error/return redirect après un if/for sans indentation
    if stripped.startswith('messages.error') or stripped.startswith('return redirect('):
        # Deviner l'indentation basée sur le contexte
        if new_lines and new_lines[-1].strip():
            prev_stripped = new_lines[-1].strip()
            # Si la ligne précédente est un if/for/elif avec :
            if prev_stripped.endswith(':') and any(prev_stripped.startswith(x) for x in ['if ', 'for ', 'elif ', 'else:']):
                # Ajouter 4 espaces
                new_lines.append('    ' + stripped)
                i += 1
                continue
    
    new_lines.append(line)
    i += 1

with open('enseignement/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Corrigé")
