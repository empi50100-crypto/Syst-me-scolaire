"""Script pour nettoyer les fichiers de vues corrompus"""
import re

def clean_view_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Si la ligne est @login_required ou @user_passes_test, vérifier si la suivante est valide
        if line.strip() in ['@login_required', '@user_passes_test']:
            # Ajouter cette ligne
            new_lines.append(line)
            i += 1
            
            # Ignorer les lignes vides suivantes
            while i < len(lines) and lines[i].strip() == '':
                new_lines.append(lines[i])
                i += 1
            
            # Si la ligne suivante est aussi un décorateur, ajouter et continuer
            while i < len(lines) and lines[i].strip() in ['@login_required', '@user_passes_test']:
                # Ne pas ajouter de doublons - juste passer à la suivante
                i += 1
            
            # Si la ligne suivante est une ligne de code (pas un def), c'est une erreur
            # On doit chercher le def qui suit
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith('def '):
                    # C'est le début de la fonction
                    new_lines.append(lines[i])
                    i += 1
                    break
                elif stripped == '' or stripped.startswith('#'):
                    new_lines.append(lines[i])
                    i += 1
                elif stripped.startswith('@'):
                    # Un autre décorateur, l'ajouter et continuer
                    new_lines.append(lines[i])
                    i += 1
                elif stripped.startswith('    if not request') or stripped.startswith('        '):
                    # Ces lignes sont mal placées, les ignorer
                    i += 1
                elif stripped.startswith('return ') or stripped.startswith('if '):
                    # Ces lignes sont mal placées aussi
                    i += 1
                else:
                    # Probablement du code normal
                    break
            continue
        
        # Sinon ajouter la ligne normalement
        new_lines.append(line)
        i += 1
    
    content_fixed = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print(f"Fichier {filepath} nettoyé")

# Nettoyer les fichiers
clean_view_file('authentification/views.py')
clean_view_file('finances/views.py')
clean_view_file('rapports/views.py')
clean_view_file('scolarite/views.py')
clean_view_file('enseignement/views.py')

print("\nTerminé!")
