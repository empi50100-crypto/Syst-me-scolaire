import re

with open('scolarite/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all problematic patterns
problems = []
for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Check for lines with 4 spaces that should be at another level
    if line.startswith('    ') and not line.startswith('        '):
        if i > 0:
            prev_stripped = lines[i-1].strip()
            prev_line = lines[i-1]
            
            # Pattern: line with 4 spaces after line ending with ':'
            if prev_stripped.endswith(':') and not prev_line.strip().startswith('#'):
                problems.append((i+1, line.rstrip(), prev_stripped[:50]))

print(f"Found {len(problems)} potential issues")
for line_num, content, prev in problems[:50]:
    print(f"Line {line_num}: {content[:60]} (after: {prev[:40]})")
