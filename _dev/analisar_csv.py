import csv
import sqlite3
import os

# Caminho do banco
db_path = os.path.join("instance", "biblioteca.db")
csv_file = "livros.csv"

print("=== ANÁLISE DO CSV ===\n")

if not os.path.exists(csv_file):
    print(f"Arquivo {csv_file} não encontrado!")
    exit(1)

# Ler CSV
with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    print(f"Cabeçalho: {header}")
    print(f"Colunas: {len(header)}\n")
    
    linhas = list(reader)
    print(f"Total de linhas no CSV: {len(linhas)}\n")

# Conectar ao banco
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Obter patrimônios já no banco
c.execute("SELECT patrimony FROM books WHERE active=1")
patrimonios_banco = set(r['patrimony'] for r in c.fetchall())
print(f"Patrimônios já no banco: {len(patrimonios_banco)}\n")

# Processar linhas
patrimonios_csv = {}
ignorados = []

for i, row in enumerate(linhas, start=2):  # +2 porque começamos do cabeçalho
    if len(row) < 2:
        continue
    
    pat = row[0].strip().upper() if len(row) > 0 else ''
    title = row[1].strip() if len(row) > 1 else ''
    
    # Verificar campos vazios
    if not pat and not title:
        ignorados.append((i, 'patrimônio e título vazios'))
        continue
    if not pat:
        ignorados.append((i, f'patrimônio vazio', title[:50]))
        continue
    if not title:
        ignorados.append((i, f'título vazio', pat))
        continue
    
    # Verificar duplicatas no CSV
    if pat in patrimonios_csv:
        patrimonios_csv[pat].append(i)
    else:
        patrimonios_csv[pat] = [i]

# Identificar ignorados
for pat, linhas_csv in patrimonios_csv.items():
    if pat in patrimonios_banco:
        for linha in linhas_csv:
            ignorados.append((linha, f'patrimônio {pat} já existe no banco'))
    elif len(linhas_csv) > 1:
        for linha in linhas_csv[1:]:  # Pular o primeiro
            ignorados.append((linha, f'patrimônio {pat} duplicado no CSV (linha {linhas_csv[0]} importada)'))

# Ordenar por linha
ignorados.sort(key=lambda x: x[0])

print("=" * 60)
print(f"LIVROS IGNORADOS: {len(ignorados)}")
print("=" * 60)

if ignorados:
    # Resumo por motivo
    motivos = {}
    for linha, motivo in ignorados:
        motivos[motivo] = motivos.get(motivo, 0) + 1
    
    print("\nRESUMO POR MOTIVO:")
    for motivo, count in sorted(motivos.items(), key=lambda x: -x[1]):
        print(f"  {motivo}: {count} livros")
    
    print("\nDETALHES (todos):")
    for linha, motivo in ignorados:
        print(f"  Linha {linha}: {motivo}")
    
    # Salvar relatório
    with open('relatorio_ignorados.txt', 'w', encoding='utf-8') as f:
        f.write(f"RELATÓRIO DE LIVROS IGNORADOS\n")
        f.write(f"Total: {len(ignorados)}\n\n")
        for linha, motivo in ignorados:
            f.write(f"Linha {linha}: {motivo}\n")
    print("\nRelatório salvo em: relatorio_ignorados.txt")
else:
    print("Nenhum livro ignorado encontrado")

conn.close()
