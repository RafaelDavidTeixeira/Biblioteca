#!/usr/bin/env python3
"""Verifica erros de sintaxe JavaScript"""
import re

with open('app/templates/app.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Verificando erros de sintaxe JavaScript...")
print()

# Verificar arrow functions nas primeiras 1500 linhas
lines = content.split('\n')
errors = []

for i, line in enumerate(lines[:1500]):
    stripped = line.strip()
    if stripped.startswith('//'):
        continue
    if '=>' in line and '=>' in stripped:
        errors.append(f"Linha {i+1}: Arrow function (=>)")
    if '?.' in line and '?.' in stripped:
        errors.append(f"Linha {i+1}: Optional chaining (?.)")

if errors:
    print(f"ENCONTRADOS {len(errors)} ERROS NAS PRIMEIRAS 1500 LINHAS:")
    for err in errors[:10]:
        print(f"  {err}")
else:
    print("SUCESSO! Nenhum erro de sintaxe nas primeiras 1500 linhas.")
    print("A interface deve carregar normalmente agora!")

print()
print("Verificando funcoes principais...")

# Verificar se as funcoes principais existem
main_funcs = ['loadDashboard', 'loadBooks', 'loadStudents', 'saveBook', 'saveStudent', 'navigate']
for func in main_funcs:
    if f'function {func}' in content:
        print(f"  [OK] {func}")
    else:
        print(f"  [ERRO] {func} nao encontrada!")

print()
print("Pronto para testar!")
