"""Corriger les problèmes d'indentation dans les fichiers de vues"""
import re

def fix_indentation(filepath):
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Chercher le pattern: if not request.user.has_module_permission
        # suivi de lignes mal indentées
        if 'if not request.user.has_module_permission' in line:
            # La ligne if est bien indentée (4 espaces)
            new_lines.append(line)
            i += 1
            
            # Les lignes suivantes (messages.error, return redirect) doivent avoir 8 espaces
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                
                # Si c'est une ligne de code mal indentée (4 espaces au lieu de 8)
                if stripped.startswith('messages.error') or stripped.startswith('return redirect'):
                    # Corriger l'indentation
                    if next_line.startswith('    '):
                        new_lines.append('        ' + stripped)
                        i += 1
                        continue
                
                # Si c'est une autre ligne de code (pas dans le if)
                if stripped and not stripped.startswith('#') and not stripped.startswith('@'):
                    # C'est probablement la fin du if - garder l'indentation normale
                    break
                
                new_lines.append(next_line)
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"  Fichier traité")

# Corriger tous les fichiers
fix_indentation('finances/views.py')

print("\nTerminé!")
