import re

with open('eleves/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix all patterns where 4 spaces should be 8 spaces
lines = content.split('\n')
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Skip empty lines and comments
    if not stripped or stripped.startswith('#'):
        fixed_lines.append(line)
        i += 1
        continue
    
    # Check if line has 4 spaces when it should have more
    if line.startswith('    ') and not line.startswith('        '):
        if i > 0:
            prev = lines[i-1].strip()
            prev_prev = lines[i-2].strip() if i > 1 else ''
            prev_prev_prev = lines[i-3].strip() if i > 2 else ''
            
            # Pattern 1: Line after 'if'/'for'/'else'/'elif' at 8 spaces level
            if prev.endswith(':') and any(k in prev for k in ['if ', 'for ', 'else:', 'elif ']):
                line = '        ' + stripped
            # Pattern 2: Line after if/for at 12 spaces level
            elif prev_prev.endswith(':') and any(k in prev_prev for k in ['if ', 'for ']):
                if prev.startswith('    '):
                    line = '            ' + stripped
            # Pattern 3: Indentation after return in if block
            elif prev.startswith('        return ') or prev.startswith('            return '):
                # Check if this should be at same level as return
                line = line  # Keep as is
            # Pattern 4: Direct messages.error/return after if condition
            elif 'if ' in prev and ':' in prev and not prev.startswith('        '):
                line = '        ' + stripped
    
    fixed_lines.append(line)
    i += 1

content = '\n'.join(fixed_lines)

with open('eleves/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed indentation patterns")
