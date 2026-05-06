import re

# Read the file
with open('app/templates/app.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original length: {len(content)} chars")

# 1. Fix spread operators: ...variable -> Object.assign({}, variable)
# This is used in JS for object spread
content = re.sub(r'\.\.\.(\w+)', r'Object.assign({}, \1)', content)

# 2. Remove any remaining backticks (template literals) - replace with regular strings
# Simple case: just text
content = content.replace('`', "'")

# 3. Fix any ${var} patterns that might remain
content = re.sub(r'\\\$\{(\w+)\}', r"'+ \1 + '", content)

# 4. Fix curly quotes (smart quotes) - replace with straight quotes
content = content.replace('\u2018', "'")  # Left single
content = content.replace('\u2019', "'")  # Right single
content = content.replace('\u201C', '"')  # Left double
content = content.replace('\u201D', '"')  # Right double

# Write back
with open('app/templates/app.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed! Verifying...")

# Verify
with open('app/templates/app.html', 'r', encoding='utf-8') as f:
    final = f.read()
    backticks = final.count('`')
    spreads = final.count('...')
    curly_single = final.count('\u2018') + final.count('\u2019')
    curly_double = final.count('\u201C') + final.count('\u201D')
    
print(f"Remaining backticks: {backticks}")
print(f"Remaining spread operators: {spreads}")
print(f"Remaining curly single quotes: {curly_single}")
print(f"Remaining curly double quotes: {curly_double}")
print(f"Final length: {len(final)} chars")
