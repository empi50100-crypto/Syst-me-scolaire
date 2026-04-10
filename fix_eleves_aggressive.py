import re

with open('eleves/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixed = []

i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line has 4 spaces when it should be at a deeper level
    if line.startswith('    ') and not line.startswith('        '):
        # Check previous line
        if i > 0:
            prev = lines[i-1]
            prev_stripped = prev.strip()
            
            # If previous line ends with ':' and contains if/for/else/elif, this needs more indentation
            if prev_stripped.endswith(':'):
                # Count indentation of previous line
                prev_indent = len(prev) - len(prev.lstrip())
                
                # If prev is at function level (4 spaces), this should be at 8
                if prev_indent == 4:
                    line = '        ' + line.strip()
                # If prev is at view level (8 spaces), this should be at 12
                elif prev_indent == 8:
                    line = '            ' + line.strip()
    
    fixed.append(line)
    i += 1

result = '\n'.join(fixed)

# More aggressive regex fixes
# Fix all instances of "    else:" followed by 4-space code
result = re.sub(r'\n    else:\n(    [^\s])', r'\n    else:\n        \1', result)

# Fix all instances of "    if" followed by 4-space code
result = re.sub(r'\n    if ([^:]+):\n(    [^\s])', r'\n    if \1:\n        \2', result)

# Fix all instances of "    elif" followed by 4-space code  
result = re.sub(r'\n    elif ([^:]+):\n(    [^\s])', r'\n    elif \1:\n        \2', result)

# Fix all instances of "    for" followed by 4-space code
result = re.sub(r'\n    for ([^:]+):\n(    [^\s])', r'\n    for \1:\n        \2', result)

with open('eleves/views.py', 'w', encoding='utf-8') as f:
    f.write(result)

print("Applied aggressive fixes")
