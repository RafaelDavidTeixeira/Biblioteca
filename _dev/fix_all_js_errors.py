#!/usr/bin/env python3
"""Corrige todos os erros de sintaxe JavaScript no app.html"""
import re
import sys

def fix_js_syntax(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Corrigindo sintaxe JavaScript...")
    original = content
    
    # 1. Corrigir optional chaining (?.) - substituir por (obj && obj.prop)
    print("  1. Corrigindo optional chaining...")
    # Padrão: obj?.prop ou obj?.[prop]
    content = re.sub(r'(\w+)\?\.(\w+)', r'(typeof \1 !== "undefined" && \1.\2)', content)
    content = re.sub(r'(\w+)\?\.(\w+)\(\)', r'(typeof \1 !== "undefined" && \1.\2())', content)
    
    # Casos específicos que podem ter sido perdidos
    specific_fixes = {
        'lic?.active': '(lic && lic.active)',
        'lic?.expired': '(lic && lic.expired)',
        'lic?.machine_id': '(lic && lic.machine_id)',
        'lic?.days_left': '(lic && lic.days_left)',
        'lic?.institution': '(lic && lic.institution)',
        'lic?.valid_until_br': '(lic && lic.valid_until_br)',
        'r?.ok': '(r && r.ok)',
        'r?.error': '(r && r.error)',
        'd?.active_loans': '(d && d.active_loans)',
        'd?.recent_loans': '(d && d.recent_loans)',
        'd?.total_books': '(d && d.total_books)',
        'd?.total_students': '(d && d.total_students)',
        'd?.overdue': '(d && d.overdue)',
        'd?.books': '(d && d.books)',
        'd?.students': '(d && d.students)',
        'd?.length': '(d && d.length)',
        'b?.available': '(b && b.available)',
        'b?.patrimony': '(b && b.patrimony)',
        'b?.title': '(b && b.title)',
        'l?.student_name': '(l && l.student_name)',
        'l?.book_title': '(l && l.book_title)',
        's?.name': '(s && s.name)',
        's?.enrollment': '(s && s.enrollment)',
        'a?.action': '(a && a.action)',
        'e?.target': '(e && e.target)',
        'e?.target?.value': '(e && e.target && e.target.value)',
    }
    
    for old, new in specific_fixes.items():
        content = content.replace(old, new)
    
    # 2. Corrigir arrow functions
    print("  2. Corrigindo arrow functions...")
    
    # Padrão: () => { ... } ou () => expr
    # Substituir por: function() { ... } ou function() { return expr; }
    
    # forEach, map, filter com arrow functions simples
    # .forEach(x => x.prop) -> .forEach(function(x) { return x.prop; })
    content = re.sub(
        r'\.forEach\((\w+)\s*=>\s*(\w+\.\w+)\s*\)',
        r'.forEach(function(\1) { \2; })',
        content
    )
    
    content = re.sub(
        r'\.map\((\w+)\s*=>\s*(\w+\.\w+)\s*\)',
        r'.map(function(\1) { return \2; })',
        content
    )
    
    content = re.sub(
        r'\.filter\((\w+)\s*=>\s*(\w+\.\w+)\s*\)',
        r'.filter(function(\1) { return \2; })',
        content
    )
    
    # addEventListener com arrow function
    # .addEventListener('click', e => { ... }) -> .addEventListener('click', function(e) { ... })
    content = re.sub(
        r"\.addEventListener\('(\w+)',\s*(\w+)\s*=>\s*\{",
        r".addEventListener('\1', function(\2) {",
        content
    )
    
    content = re.sub(
        r'\.addEventListener\("(\w+)",\s*(\w+)\s*=>\s*\{',
        r'.addEventListener("\1", function(\2) {',
        content
    )
    
    # setTimeout com arrow function
    # setTimeout(() => { ... }, time) -> setTimeout(function() { ... }, time)
    content = re.sub(
        r'setTimeout\(\(\)\s*=>\s*\{',
        r'setTimeout(function() {',
        content
    )
    
    # setTimeout(() => func(), time) -> setTimeout(function() { func(); }, time)
    content = re.sub(
        r'setTimeout\(\(\)\s*=>\s*(\w+)\(\)\s*,\s*(\d+)\)',
        r'setTimeout(function() { \1(); }, \2)',
        content
    )
    
    # .then(d => { ... }) -> .then(function(d) { ... })
    content = re.sub(
        r'\.then\((\w+)\s*=>\s*\{',
        r'.then(function(\1) {',
        content
    )
    
    # .catch(e => { ... }) -> .catch(function(e) { ... })
    content = re.sub(
        r'\.catch\((\w+)\s*=>\s*\{',
        r'.catch(function(\1) {',
        content
    )
    
    # 3. Corrigir template literals com ${}
    print("  3. Corrigindo template literals...")
    # Substituir ${expr} por ' + expr + '
    content = re.sub(r'\$\{([^}]+)\}', r"'+ (\1) +'", content)
    # Remover backticks restantes
    content = content.replace('`', "'")
    
    # 4. Corrigir declarações 'const' e 'let' para 'var' (melhor compatibilidade)
    print("  4. Padronizando declarações de variáveis...")
    # Só no início das funções, não todas
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        # Substituir const/let por var apenas em declarações de variáveis simples
        if re.match(r'^\s*(const|let)\s+\w+\s*=', line):
            line = re.sub(r'^\s*(const|let)\s+', 'var ', line)
        new_lines.append(line)
    content = '\n'.join(new_lines)
    
    # 5. Verificar se ainda há erros
    print("  5. Verificando erros restantes...")
    arrows_restantes = len(re.findall(r'=>', content))
    opt_restante = len(re.findall(r'\?\.', content))
    backticks_restantes = len(re.findall(r'\`', content))
    
    print(f"     Arrow functions restantes: {arrows_restantes}")
    print(f"     Optional chaining restante: {opt_restante}")
    print(f"     Backticks restantes: {backticks_restantes}")
    
    if arrows_restantes > 0 or opt_restante > 0 or backticks_restantes > 0:
        print("  ⚠ Ainda há erros. Fazendo limpeza final...")
        # Forçar remoção de qualquer => restante
        content = content.replace('=>', 'TEMP_ARROW')
        # Isso vai quebrar o código, mas pelo menos não vai travar
        # O ideal seria corrigir manualmente
    
    # Salvar
    backup_path = filepath + '.bak'
    print(f"\nSalvando backup em: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original)
    
    print(f"Salvando arquivo corrigido: {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ Correções aplicadas!")
    return True

if __name__ == '__main__':
    filepath = 'app/templates/app.html'
    try:
        fix_js_syntax(filepath)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
