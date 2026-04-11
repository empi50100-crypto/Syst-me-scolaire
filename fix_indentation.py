"""Corriger les erreurs d'indentation dans authentification/views.py"""
import re

# Lire le fichier
with open('authentification/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern pour trouver et corriger:
# @login_required
#     if not request.user.has_module_permission("...", "...")
#         messages.error(...)
#         return redirect(...)
# def func_name(request, ...):
#
# Devient:
# @login_required
# def func_name(request, ...):
#     if not request.user.has_module_permission("...", "..."):
#         messages.error(...)
#         return redirect(...)

lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Chercher @login_required suivi de lignes mal indentées avec "if not request.user.has_module_permission"
    if '@login_required' in line and i + 1 < len(lines):
        # Ajouter @login_required
        new_lines.append(line)
        
        # Vérifier si la ligne suivante a une indentation de 4 espaces ET contient "if not request.user.has_module_permission"
        if i + 1 < len(lines) and lines[i + 1].startswith('    if not request.user.has_module_permission'):
            # C'est notre cas problématique
            # Collecter les lignes de la vérification de permission
            perm_lines = []
            j = i + 1
            while j < len(lines) and lines[j].startswith('        '):
                perm_lines.append(lines[j])
                j += 1
            
            # La prochaine ligne devrait être "def func_name"
            if j < len(lines) and lines[j].startswith('    def '):
                # C'est le cas problématique
                func_line = lines[j]
                # Remplacer "    def func_name" par "def func_name" 
                new_lines.append(func_line)
                i = j + 1
                
                # Maintenant ajouter les lignes de permission avec la bonne indentation
                for pl in perm_lines:
                    # Réduire l'indentation de 4 espaces
                    if pl.startswith('        '):
                        pl = pl[4:]
                    new_lines.append(pl)
                
                continue
        
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

content_new = '\n'.join(new_lines)

with open('authentification/views.py', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("Fichier authentification/views.py corrigé")
