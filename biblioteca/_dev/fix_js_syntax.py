import re

# Read the file
with open('app/templates/app.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original length: {len(content)} chars")

# 1. Fix template literals - replace `${var}` with ' + var + '
def replace_template_literals(match):
    s = match.group(0)
    # Extract content between backticks
    inner = s[1:-1]  # Remove backticks
    # Replace ${...} with ' + ... + '
    inner = re.sub(r'\$\{([^}]+)\}', r"'+ (\1) +'", inner)
    # Replace remaining backticks with quotes
    result = "'" + inner + "'"
    return result

# Find and replace template literals
content = re.sub(r'\`[^\`]*\$\{[^}]+\}[^\`]*\`', replace_template_literals, content)

# 2. Fix simple template literals without ${}
content = content.replace('`', "'")

# 3. Fix spread operators in objects: {...x} -> Object.assign({}, x)
content = re.sub(r'\{\.\.\.(\w+)\}', r'Object.assign({}, \1)', content)

# 4. Fix spread in function calls: ...opts -> Object.assign({}, opts)
# This is trickier - look for ...variable in function call context
# For now, just replace common patterns
content = re.sub(r'fetch\(url,\s*\.\.\.opts\)', r'fetch(url, Object.assign({}, opts))', content)

# 5. Fix any remaining backticks
backtick_count = content.count('`')
print(f"Remaining backticks: {backtick_count}")

# 6. Fix curly quotes in numbers (e.g., 1500, 2000)
# Replace curly quotes around numbers
content = re.sub(r'[\u2018\u2019\u201C\u201D](\d+)[\u2018\u2019\u201C\u201D]', r'\1', content)

# 7. Fix curly quotes in strings
content = content.replace('\u2018', "'").replace('\u2019', "'")
content = content.replace('\u201C', '"').replace('\u201D', '"')

# Write back
with open('app/templates/app.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed! Verifying...")

# Verify
with open('app/templates/app.html', 'r', encoding='utf-8') as f:
    final = f.read()
    remaining_backticks = final.count('`')
    remaining_spread = final.count('...')
    print(f"Remaining backticks: {remaining_backticks}")
    print(f"Remaining spread operators: {remaining_spread}")
    
    # Check for curly quotes
    import unicodedata
    curly_count = sum(1 for c in final if unicodedata.category(c) == 'Pd' and c not in "'\"")
    print(f"Remaining curly quotes: {curly_count}")
