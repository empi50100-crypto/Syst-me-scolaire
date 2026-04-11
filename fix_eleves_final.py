import re

with open('scolarite/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Comprehensive regex patterns to fix all known issues

# Pattern 1: if/elif/else/for at 4 spaces followed by code at 4 spaces
# This fixes cases like "    if x:\n    code" where "code" should be at 8 spaces
content = re.sub(
    r'\n    (if |elif |else:\n)(    )?([a-z])',
    r'\n    \1        \3',
    content
)

# Pattern 2: Nested ifs with 4 spaces that should be at 8
content = re.sub(
    r'\n        (if |elif )([^\n]+:\n)(    )?([a-z])',
    r'\n        \1\2            \4',
    content
)

# Pattern 3: Fix specific problematic patterns
# "    if x:\n    if y:\n    code" -> "    if x:\n        if y:\n    code"
content = re.sub(
    r'(\n    if [^:]+:\n)(    if )',
    r'\1        \2',
    content
)

# Pattern 4: Fix else: at wrong level
content = re.sub(
    r'(\n        if [^\n]+\n)(    else:\n)(    [a-z])',
    r'\1        \2            \3',
    content
)

# Pattern 5: Fix for loops at wrong level
content = re.sub(
    r'(\n    for [^\n]+\n)(    [a-z])',
    r'\1        \2',
    content
)

# Pattern 6: Fix messages.error/return at wrong level
content = re.sub(
    r'(messages\.(error|success|warning)\([^)]+\)\n)(    return )',
    r'\1        \3',
    content
)

# Pattern 7: Fix "else:" followed by wrong indent
content = re.sub(
    r'(\n    else:\n)(    [a-z_])',
    r'\1        \2',
    content
)

# Pattern 8: Fix nested else: at wrong level
content = re.sub(
    r'(\n        else:\n)(    [a-z_])',
    r'\1            \2',
    content
)

# Pattern 9: Fix elif at function level followed by wrong indent
content = re.sub(
    r'(\n    elif [^:]+:\n)(    [a-z])',
    r'\1        \2',
    content
)

# Pattern 10: Remove extra indentation on statements that are at top of if blocks
# "        if x:\n    code" -> "        if x:\n            code"  
content = re.sub(
    r'(        if [^:]+:\n)(    [a-z])',
    r'\1            \2',
    content
)

with open('scolarite/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied all regex fixes")
