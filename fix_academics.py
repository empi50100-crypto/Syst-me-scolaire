"""Corriger le fichier enseignement/views.py"""
import re

with open('enseignement/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger tous les return redirect(...):
pattern = r"return redirect\([^)]+\):"
content = re.sub(pattern, lambda m: m.group().rstrip(':'), content)

with open('enseignement/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Corrigé")
