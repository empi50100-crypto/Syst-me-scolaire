"""Script pour corriger les erreurs d'indentation dans les vues"""
import re

def fix_file(filepath, module_code):
    """Corriger les erreurs d'indentation dans un fichier de vues"""
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Chercher le motif problématique:
        # @login_required
        #     if not request.user.has_module_permission(...)
        #         messages.error(...)
        #         return redirect(...)
        # def func_name(...):
        
        if '@login_required' in line and i + 1 < len(lines):
            new_lines.append(line.strip())
            i += 1
            
            # Vérifier si la ligne suivante commence par 4 espaces (mauvais)
            if i < len(lines) and lines[i].startswith('    if not request.user'):
                # Collecter les lignes de permission mal indentées
                perm_check_lines = []
                while i < len(lines) and (lines[i].startswith('    if not request.user') or 
                                          lines[i].startswith('        ')):
                    perm_check_lines.append(lines[i])
                    i += 1
                
                # Maintenant devrait venir "def func_name"
                if i < len(lines) and lines[i].strip().startswith('def '):
                    func_def = lines[i].strip()
                    # Corriger l'indentation
                    # - Enlever les 4 espaces de "def func_name"
                    # - Réduire de 4 espaces les lignes de permission
                    
                    # Ajouter la définition de fonction correctement indentée
                    new_lines.append(func_def)
                    i += 1
                    
                    # Ajouter les lignes de vérification avec la bonne indentation (4 espaces)
                    for pl in perm_check_lines:
                        if pl.startswith('        '):
                            pl = '    ' + pl[8:]
                        elif pl.startswith('    if not request.user'):
                            pass  # Garder tel quel (4 espaces)
                        new_lines.append(pl)
                    
                    continue
        
        new_lines.append(line)
        i += 1
    
    content_new = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_new)
    
    print(f"  Fichier corrigé")

# Corriger les fichiers
base_path = r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole'
fix_file(f'{base_path}/authentification/views.py', 'user_list')
fix_file(f'{base_path}/finances/views.py', 'annee_scolaire')
fix_file(f'{base_path}/rapports/views.py', 'rapport_academique')
fix_file(f'{base_path}/scolarite/views.py', 'discipline')
fix_file(f'{base_path}/enseignement/views.py', 'examen_list')

print("\nTerminé!")
