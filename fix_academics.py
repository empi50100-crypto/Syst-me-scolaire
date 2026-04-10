"""Corriger le fichier academics/views.py"""
import re

with open('academics/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger tous les return redirect(...):
pattern = r"return redirect\([^)]+\):"
content = re.sub(pattern, lambda m: m.group().rstrip(':'), content)

with open('academics/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Corrigé")
