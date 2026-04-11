import re

with open('scolarite/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Empty lines and comments - keep as is
    if not stripped or stripped.startswith('#'):
        fixed_lines.append(line)
        i += 1
        continue
    
    # Check for lines with 4 spaces that need to be 8 or 12 spaces
    if line.startswith('    ') and not line.startswith('        '):
        if i > 0:
            prev_stripped = lines[i-1].strip()
            prev_line = lines[i-1]
            prev_prev_stripped = lines[i-2].strip() if i > 1 else ''
            
            # Pattern: if/elif/for/else at function level (4 spaces) followed by code
            if prev_stripped.endswith(':') and any(k in prev_stripped for k in ['if ', 'for ', 'else:', 'elif ']):
                # Check if prev is at function level (4 spaces)
                if prev_line.startswith('    ') and not prev_line.startswith('        '):
                    line = '        ' + stripped
            # Pattern: if at 8 spaces followed by code that needs 12 spaces
            elif prev_line.startswith('        ') and not prev_line.startswith('            '):
                if prev_stripped.endswith(':') and any(k in prev_stripped for k in ['if ', 'for ', 'else:', 'elif ']):
                    line = '            ' + stripped
    
    fixed_lines.append(line)
    i += 1

result = ''.join(fixed_lines)

# Additional regex fixes for specific patterns
# Fix messages.error followed by return on same line
result = re.sub(r'(messages\.[a-z]+\([^)]+\)\s*)\n(\s*return )', r'\1\n\2', result)

# Fix statements at wrong indentation levels
# Pattern: else: followed by statement with 4 spaces
result = re.sub(r'(\n    else:\n)(    [a-z])', r'\1        \2', result)

# Pattern: if condition: followed by statement with 4 spaces (at function level)
result = re.sub(r'(\n    if [^:]+:\n)(    messages)', r'\1        \2', result)
result = re.sub(r'(\n    if [^:]+:\n)(    return)', r'\1        \2', result)
result = re.sub(r'(\n    if [^:]+:\n)(    eleves)', r'\1        \2', result)
result = re.sub(r'(\n    if [^:]+:\n)(    documents)', r'\1        \2', result)
result = re.sub(r'(\n    if [^:]+:\n)(    parents)', r'\1        \2', result)

# Pattern: elif followed by statement with 4 spaces
result = re.sub(r'(\n    elif [^:]+:\n)(    [a-z])', r'\1        \2', result)

# Pattern: for loop followed by statement with 4 spaces
result = re.sub(r'(\n    for [^:]+:\n)(    [a-z])', r'\1        \2', result)

with open('scolarite/views.py', 'w', encoding='utf-8') as f:
    f.write(result)

print("Applied comprehensive fixes")
