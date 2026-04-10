"""Script simple pour corriger les fichiers de vues"""
import re

def fix_file(filepath):
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Répéter jusqu'à ce qu'il n'y ait plus d'erreurs
    for _ in range(5):
        lines = content.split('\n')
        new_lines = []
        changed = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Corriger: return redirect puis (sur la ligne suivante)
            if stripped.startswith('return redirect') or stripped.startswith('return redirect,'):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('(') and not stripped.endswith('('):
                        content = content.replace(line + '\n' + lines[i + 1], stripped + ' ' + next_line, 1)
                        changed = True
                        break
            
            # Corriger: messages.error ou return redirect avec 4 espaces au lieu de 8
            if stripped.startswith('messages.error') or stripped.startswith('return redirect(\''):
                if line.startswith('    ') and not line.startswith('        '):
                    content = content.replace(line, '        ' + stripped, 1)
                    changed = True
                    break
            
            i += 1
        
        if not changed:
            break
    
    # Supprimer les @user_passes_test résiduels
    content = re.sub(r'@user_passes_test\s*\n\s*\n', '\n', content)
    content = re.sub(r'@user_passes_test\s*\n', '\n', content)
    
    # Supprimer les @login_required doubles
    while '@login_required\n@login_required' in content:
        content = content.replace('@login_required\n@login_required', '@login_required')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Fichier traité")

# Corriger tous les fichiers
fix_file('finances/views.py')
fix_file('rapports/views.py')
fix_file('academics/views.py')
fix_file('eleves/views.py')

print("\nTerminé!")
