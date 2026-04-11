"""Corriger les erreurs d'indentation courantes dans enseignement/views.py"""
import re

with open('enseignement/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger les patterns courants
# 1. messages.error/return redirect après if/for/else sans indentation
patterns = [
    # if ...:\n    messages.error -> indentation 4 espaces
    (r'((?:^|\n)(?:    )*(?:if |for |elif ).*?:)\n((?:    )*)messages\.error', r'\1\n\2    messages.error'),
    (r'((?:^|\n)(?:    )*(?:if |for |elif ).*?:)\n((?:    )*)return redirect', r'\1\n\2    return redirect'),
    # else:\n    messages.error -> indentation 4 espaces
    (r'((?:^|\n)(?:    )*)else:\n((?:    )*)messages\.error', r'\1else:\n\2    messages.error'),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

with open('enseignement/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Corrigé")
