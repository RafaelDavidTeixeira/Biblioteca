import sqlite3
import csv
import io

db_path = 'instance/biblioteca.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get all books in database
c.execute("SELECT patrimony FROM books")
existing_patrimonies = set(row[0] for row in c.fetchall())
print(f"Total de livros no banco: {len(existing_patrimonies)}\n")

# Ask for CSV file path
import sys
if len(sys.argv) > 1:
    csv_path = sys.argv[1]
else:
    csv_path = 'livros_teste.csv'  # default file

print(f"Analisando arquivo: {csv_path}\n")

try:
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    reader = csv.DictReader(io.StringIO(content))
    total = 0
    vazios = 0
    duplicados_banco = 0
    duplicados_csv = 0
    erros = 0
    pat_seen = {}
    
    for i, row in enumerate(reader, 1):
        total += 1
        pat = (row.get('patrimonio') or row.get('patrimônio') or row.get('PAT') or '').strip().upper()
        title = (row.get('titulo') or row.get('título') or row.get('title') or '').strip()
        
        if not pat or not title:
            vazios += 1
            print(f"Linha {i}: patrimônio ou título vazio - PAT: '{pat}', Título: '{title}'")
            continue
        
        if pat in pat_seen:
            duplicados_csv += 1
            print(f"Linha {i}: patrimônio {pat} duplicado no CSV (primeira vez na linha {pat_seen[pat]})")
            continue
        
        pat_seen[pat] = i
        
        if pat in existing_patrimonies:
            duplicados_banco += 1
            print(f"Linha {i}: patrimônio {pat} já existe no banco")
            continue
    
    print(f"\n=== RESUMO ===")
    print(f"Total de linhas: {total}")
    print(f"Itens ignorados (vazios): {vazios}")
    print(f"Itens ignorados (duplicados no CSV): {duplicados_csv}")
    print(f"Itens ignorados (já no banco): {duplicados_banco}")
    print(f"Total ignorados: {vazios + duplicados_csv + duplicados_banco}")
    
except FileNotFoundError:
    print(f"Arquivo {csv_path} não encontrado.")
    print("Uso: python analisar_rejeitados.py <caminho_do_csv>")
except Exception as e:
    print(f"Erro: {e}")

conn.close()
