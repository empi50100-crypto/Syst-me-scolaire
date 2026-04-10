import re

with open('academics/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all patterns where a line with 4 spaces should be inside an if statement
# This regex finds: if condition: followed by a line with 4 spaces that should be 8 spaces
content = re.sub(
    r'(\n    if [^:\n]+:\n)(    messages\.error\([^)]+\))',
    r'\1        \2',
    content
)
content = re.sub(
    r'(\n    if [^:\n]+:\n)(    return redirect\([^)]+\))',
    r'\1        \2',
    content
)
content = re.sub(
    r'(\n    elif [^:\n]+:\n)(    messages\.error\([^)]+\))',
    r'\1        \2',
    content
)
content = re.sub(
    r'(\n    elif [^:\n]+:\n)(    return redirect\([^)]+\))',
    r'\1        \2',
    content
)
content = re.sub(
    r'(\n    else:\n)(    \w+)',
    r'\1        \2',
    content
)
content = re.sub(
    r'(\n    for [^:\n]+:\n)(    \w+)',
    r'\1        \2',
    content
)

# Fix specific patterns that are known issues
# messages.error followed by return redirect
content = re.sub(
    r'(messages\.error\([^)]+\)\n)(    return redirect\([^)]+\))',
    r'\1        \2',
    content
)

with open('academics/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed patterns")
