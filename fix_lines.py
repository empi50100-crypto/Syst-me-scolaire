"""Corriger systematiquement academics/views.py"""
import re

with open('academics/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger les lignes fusionnees
content = re.sub(r'(messages\.error.*?)(        return redirect)', r'\1\n\2', content)

# Corriger les return redirect mal indentés
content = re.sub(r'^        return redirect\(', '            return redirect(', content, flags=re.MULTILINE)

# Corriger les messages.error mal indentés
content = re.sub(r'^        messages\.error\(', '            messages.error(', content, flags=re.MULTILINE)

with open('academics/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Corrige")
