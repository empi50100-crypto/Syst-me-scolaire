import re

with open('scolarite/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances of the pattern with proper indentation
# Pattern: messages.error/return with 4 spaces after if/else:
content = re.sub(
    r'(\n        if existing_doc:\n)(    messages\.error)',
    r'\1            \2',
    content
)

# Fix all patterns with 4 spaces before statements that should have 8 or 12
lines = content.split('\n')
fixed = []
for i, line in enumerate(lines):
    if line.startswith('    ') and not line.startswith('        '):
        if i > 0:
            prev = lines[i-1].strip()
            if prev.endswith(':') and ('if ' in prev or 'else:' in prev or 'elif ' in prev or 'for ' in prev):
                line = '        ' + line.strip()
    fixed.append(line)

content = '\n'.join(fixed)

with open('scolarite/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed")
