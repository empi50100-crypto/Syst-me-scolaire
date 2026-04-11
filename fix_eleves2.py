import re

with open('scolarite/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all lines with only 4 spaces before statements that should have more
lines = content.split('\n')
fixed = []
for i, line in enumerate(lines):
    if line.startswith('    ') and not line.startswith('        '):
        if i > 0:
            prev = lines[i-1].strip()
            prev2 = lines[i-2].strip() if i > 1 else ''
            if prev.endswith(':') and ('if ' in prev or 'else:' in prev or 'elif ' in prev or 'for ' in prev):
                line = '        ' + line.strip()
            elif prev2.endswith(':') and ('if ' in prev2 or 'for ' in prev2):
                line = '            ' + line.strip()
    fixed.append(line)

content = '\n'.join(fixed)

# Fix all instances of messages.error with wrong indentation after if/else
content = re.sub(
    r'(if existing_doc:\n)(    messages\.error)',
    r'\1                            \2',
    content
)

with open('scolarite/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed")
