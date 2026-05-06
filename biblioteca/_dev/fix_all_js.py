#!/usr/bin/env python3
"""Corrige erros de sintaxe JavaScript no app.html"""
import re

with open('app/templates/app.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Corrigindo sintaxe JavaScript...")

# 1. Corrigir optional chaining (?.) - substituir por (obj && obj.prop)
# Padrão: obj?.prop -> (obj && obj.prop)
def fix_optional_chaining(text):
    # Match: word?.word ou word?.word[...]
    pattern = r'(\w+)\?\.(\w+)'
    def replace(match):
        obj = match.group(1)
        prop = match.group(2)
        return f'({obj} && {obj}.{prop})'
    return re.sub(pattern, replace, text)

# Corrigir padrões específicos primeiro
replacements_opt = [
    ('lic?.active', '(lic && lic.active)'),
    ('lic?.expired', '(lic && lic.expired)'),
    ('lic?.machine_id', '(lic && lic.machine_id)'),
    ('lic?.days_left', '(lic && lic.days_left)'),
    ('lic?.institution', '(lic && lic.institution)'),
    ('lic?.valid_until_br', '(lic && lic.valid_until_br)'),
    ('r?.ok', '(r && r.ok)'),
    ('r?.error', '(r && r.error)'),
    ('d?.active_loans', '(d && d.active_loans)'),
    ('d?.recent_loans', '(d && d.recent_loans)'),
    ('d?.total_books', '(d && d.total_books)'),
    ('d?.total_students', '(d && d.total_students)'),
    ('d?.overdue', '(d && d.overdue)'),
    ('d?.books', '(d && d.books)'),
    ('d?.students', '(d && d.students)'),
    ('d?.length', '(d && d.length)'),
    ('b?.available', '(b && b.available)'),
    ('b?.patrimony', '(b && b.patrimony)'),
    ('b?.title', '(b && b.title)'),
    ('l?.student_name', '(l && l.student_name)'),
    ('l?.book_title', '(l && l.book_title)'),
    ('s?.name', '(s && s.name)'),
    ('s?.enrollment', '(s && s.enrollment)'),
    ('a?.action', '(a && a.action)'),
    ('e?.target', '(e && e.target)'),
]

content_new = content
for old, new in replacements_opt:
    content_new = content_new.replace(old, new)

# 2. Corrigir arrow functions (=>) em callbacks
# Padrão simples: .forEach(x => { ... }) -> .forEach(function(x) { ... })
# Isso é complexo, vamos fazer substituições específicas

# Padrão: setTimeout(() => ..., tempo) -> setTimeout(function() { ... }, tempo)
content_new = re.sub(
    r'setTimeout\(\(\)\s*=>\s*({[^}]+})\s*,\s*(\d+)\)',
    r'setTimeout(function() \1, \2)',
    content_new
)

# Padrão: () => func() -> function() { func(); }
content_new = re.sub(
    r'\(\)\s*=>\s*(\w+\([^)]*\))',
    r'function() { \1; }',
    content_new
)

# Padrão: x => x.prop -> function(x) { return x.prop; }
# Isso é muito complexo para regex, vamos deixar para edições manuais

print("Substituindo arrow functions específicas...")

# Substituir padrões comuns de arrow functions
arrow_replacements = [
    # forEach patterns
    (r'\.forEach\((\w+)\s*=>\s*{', r'.forEach(function(\1) {'),
    (r'\.forEach\((\w+)\s*=>\s*(\w+\([^)]*\))\);', r'.forEach(function(\1) { \2; });'),
    (r'\.forEach\((\w+)\s*=>\s*(\w+\.\w+)\s*\);', r'.forEach(function(\1) { \2; });'),
    
    # map patterns  
    (r'\.map\((\w+)\s*=>\s*{', r'.map(function(\1) {'),
    (r'\.map\((\w+)\s*=>\s*(\'[^\']*\'|\"[^\"]*\")\s*\+', r'.map(function(\1) { return \2 +'),
    
    # addEventListener patterns
    (r'addEventListener\(\'(\w+)\',\s*\(\)\s*=>\s*{', r'addEventListener(\'\1\', function() {'),
    (r'addEventListener\(\'(\w+)\',\s*\((\w+)\)\s*=>\s*{', r'addEventListener(\'\1\', function(\2) {'),
]

for pattern, replacement in arrow_replacements:
    content_new = re.sub(pattern, replacement, content_new)

# 3. Corrigir template literals com ${} (se houver)
# Substituir por concatenação simples
content_new = content_new.replace('${b.patrimony)', '(b.patrimony)')
content_new = content_new.replace('${b.title)', '(b.title)')
content_new = content_new.replace('${b.author)', '(b.author)')
content_new = content_new.replace('${l.event)', '(l.event)')
content_new = content_new.replace('${l.student_name)', '(l.student_name)')
content_new = content_new.replace('${l.book_title)', '(l.book_title)')
content_new = content_new.replace('${s.name)', '(s.name)')
content_new = content_new.replace('${s.enrollment)', '(s.enrollment)')
content_new = content_new.replace('${i+1)', '(i+1)')

# 4. Remover qualquer backtick restante
content_new = content_new.replace('`', "'")

with open('app/templates/app.html', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("Correções aplicadas!")
print("Verifique o arquivo e teste novamente.")
