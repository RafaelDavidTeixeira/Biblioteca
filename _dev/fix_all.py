import re

# Corrigir database.py - adicionar commit() em todas as funções que fazem alterações
with open('app/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Padrão: encontrar funções com "with get_conn() as conn:" que não têm conn.commit()
# Vamos adicionar conn.commit() antes do fechamento do with
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Se a linha tem "with get_conn() as conn:" ou "with get_conn() as c:"
    if 'with get_conn() as ' in line and ('conn' in line or 'c' in line):
        # Encontrar o nível de indentação
        indent = len(line) - len(line.lstrip())
        conn_var = 'conn' if 'conn' in line else 'c'
        
        # Procurar pelo final do bloco (próxima linha com menor indentação)
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            if next_line.strip() == '':
                j += 1
                continue
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_indent <= indent and next_line.strip() != '':
                break
            j += 1
        
        # Adicionar conn.commit() antes do final do bloco (se houver operações de escrita)
        block_lines = lines[i+1:j]
        block_text = '\n'.join(block_lines)
        if any(op in block_text for op in ['INSERT', 'UPDATE', 'DELETE', 'execute("']):
            # Adicionar commit antes do final
            commit_line = ' ' * (indent + 4) + f'{conn_var}.commit()'
            # Verificar se já não tem commit
            if f'{conn_var}.commit()' not in block_text:
                # Inserir antes da última linha do bloco
                if block_lines:
                    # Adicionar após a última operação
                    new_lines.extend(block_lines)
                    new_lines.append(commit_line)
                    i = j
                    continue
    
    i += 1

# Escrever arquivo corrigido
with open('app/database.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("database.py corrigido!")
