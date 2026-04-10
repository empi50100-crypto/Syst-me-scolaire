import re

with open('academics/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Skip lines that are just whitespace or comments at function level
    if line.strip() == '' or line.strip().startswith('#'):
        fixed_lines.append(line)
        i += 1
        continue
    
    # Check if this line has wrong indentation (4 spaces when it should be 8 or 12)
    if line.startswith('    ') and not line.startswith('        '):
        if i > 0:
            prev = lines[i-1].strip()
            prev_prev = lines[i-2].strip() if i > 1 else ''
            
            # Pattern 1: messages.error/return after if condition
            if prev.endswith(':') and ('if ' in prev or 'elif ' in prev or 'else:' in prev):
                # Indent this line by 4 more spaces
                line = '        ' + line.strip()
            
            # Pattern 2: messages.error/return after else: at wrong level
            if 'else:' in prev and not prev.startswith('        '):
                line = '        ' + line.strip()
            
            # Pattern 3: statements after for loop
            if prev.startswith('for ') and not prev.startswith('        '):
                line = '        ' + line.strip()
    
    fixed_lines.append(line)
    i += 1

# Now fix all the specific patterns we know about
result = '\n'.join(fixed_lines)

# Fix messages.error followed by return redirect (same line issues)
result = re.sub(
    r'(messages\.(?:error|success)\([^)]+\))\s*\n(\s*return redirect)',
    r'\1\n\2',
    result
)

# Fix statements that should be inside else blocks
result = re.sub(
    r'(\n\s*else:\n)(\s{4})(\w+)',
    r'\1\2        \3',
    result
)

with open('academics/views.py', 'w', encoding='utf-8') as f:
    f.write(result)

print("Applied fixes")
