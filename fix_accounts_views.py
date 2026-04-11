"""Reconstruire le fichier authentification/views.py correctement"""
import re

filepath = 'authentification/views.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Diviser en lignes
lines = content.split('\n')

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Corriger les cas où @login_required est suivi directement par du code mal indenté
    # ou par un autre @login_required
    if line.strip() == '@login_required':
        # Regarder les lignes suivantes
        next_lines = []
        j = i + 1
        while j < len(lines) and lines[j].strip() in ['', '@login_required', '@user_passes_test'] or \
              (j > i + 1 and (lines[j].startswith('    return ') or 
                              lines[j].startswith('    if not request.user'))):
            if lines[j].strip() in ['', '@login_required', '@user_passes_test']:
                next_lines.append(lines[j])
            else:
                next_lines.append(lines[j])
            j += 1
        
        # Si on a trouvé un motif incorrect, le corriger
        if next_lines and any('return' in l or 'if not request.user' in l for l in next_lines):
            # Ajouter @login_required et continuer
            new_lines.append('@login_required')
            i += 1
            continue
    
    new_lines.append(line)
    i += 1

# Une approche plus directe: chercher les lignes mal indentées après @login_required
content_fixed = '\n'.join(new_lines)

# Pattern pour trouver les groupes de @login_required dupliqués ou mal estructurés
pattern = r'(@login_required\n)(\n|@login_required\n|    (return|if not request\.user))'
content_fixed = re.sub(pattern, r'\1\n', content_fixed)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print(f"Fichier {filepath} partiellement corrigé")
