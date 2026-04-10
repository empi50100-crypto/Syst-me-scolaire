"""Script pour reconstruire les fichiers de vues corrompus"""
import re

def rebuild_file(filepath):
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer les sauts de ligne multiples par des sauts simples
    # Mais préserver les séparationslogiques entre fonctions
    
    # Diviser en lignes
    lines = content.split('\n')
    
    # Enlever les lignes vides consécutives (garder max 2)
    new_lines = []
    empty_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            empty_count += 1
            if empty_count <= 2:
                new_lines.append(line)
        else:
            empty_count = 0
            new_lines.append(line)
    
    # Rejoindre
    content = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Phase 1 terminée: {len(new_lines)} lignes")

# Traiter le fichier accounts/views.py en premier
rebuild_file('accounts/views.py')

# Vérifier la syntaxe
import subprocess
result = subprocess.run(
    ['python', '-c', 'import ast; ast.parse(open("accounts/views.py").read())'],
    capture_output=True, text=True, cwd='.'
)
print(f"\nVérification syntaxe: {result.returncode == 0}")
if result.returncode != 0:
    print(f"Erreur: {result.stderr[:500]}")
