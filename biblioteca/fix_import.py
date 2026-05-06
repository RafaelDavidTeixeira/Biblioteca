import csv
import io
import sqlite3
import os

def analisar_e_corrigir():
    # Encontrar o CSV mais recente na pasta
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("Nenhum arquivo CSV encontrado na pasta atual.")
        print("Por favor, coloque o arquivo CSV na pasta D:\\Projetos DEV\\biblioteca")
        return
    
    # Usar o CSV mais recente
    csv_file = max(csv_files, key=os.path.getmtime)
    print(f"Analisando: {csv_file}\n")
    
    # Ler o CSV
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Verificar se tem cabeçalho
    linhas = content.split('\n')
    primeira_linha = linhas[0].lower()
    
    # Se a primeira linha parecer um cabeçalho, pular
    tem_cabecalho = any(col in primeira_linha for col in ['patrimonio', 'titulo', 'title', 'author'])
    print(f"Tem cabeçalho: {tem_cabecalho}")
    print(f"Primeira linha: {linhas[0][:100]}...\n")
    
    # Ler como CSV
    reader = csv.reader(io.StringIO(content))
    
    if tem_cabecalho:
        cabecalho = next(reader)
        print(f"Colunas no cabeçalho ({len(cabecalho)}): {cabecalho}\n")
    
    # Conectar ao banco
    db_path = os.path.join("instance", "biblioteca.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Obter patrimônios já existentes
    c.execute("SELECT patrimony FROM books WHERE active=1")
    patrimonios_existentes = set(r['patrimony'] for r in c.fetchall())
    print(f"Patrimônios já no banco: {len(patrimonios_existentes)}\n")
    
    # Analisar linhas
    importados = 0
    ignorados = []
    patrimonios_csv = set()
    
    for i, row in enumerate(reader, 2 if tem_cabecalho else 1):
        # Pular linhas vazias
        if not row or (len(row) == 1 and not row[0].strip()):
            continue
        
        # Assumindo formato: patrimonio, titulo, autor, isbn, categoria, editora, year, quantity
        try:
            pat = row[0].strip().upper() if len(row) > 0 else ''
            title = row[1].strip() if len(row) > 1 else ''
            author = row[2].strip() if len(row) > 2 else ''
            isbn = row[3].strip() if len(row) > 3 else ''
            category = row[4].strip() if len(row) > 4 else ''
            publisher = row[5].strip() if len(row) > 5 else ''
            year = row[6].strip() if len(row) > 6 else ''
            quantity = row[7].strip() if len(row) > 7 else '1'
            
            # Verificar campos obrigatórios
            if not pat and not title:
                ignorados.append((i, 'patrimonio e título vazios', row))
                continue
            if not pat:
                ignorados.append((i, 'patrimonio vazio', row))
                continue
            if not title:
                ignorados.append((i, 'título vazio', row))
                continue
            
            # Verificar duplicatas no CSV
            if pat in patrimonios_csv:
                ignorados.append((i, f'patrimonio duplicado no CSV: {pat}', row))
                continue
            
            # Verificar se já existe no banco
            if pat in patrimonios_existentes:
                ignorados.append((i, f'patrimonio já existe no banco: {pat}', row))
                continue
            
            patrimonios_csv.add(pat)
            importados += 1
            
        except Exception as e:
            ignorados.append((i, f'erro ao processar: {e}', row))
    
    print(f"=== RESULTADO ===")
    print(f"Linhas processadas: {importados + len(ignorados)}")
    print(f"Prontas para importar: {importados}")
    print(f"Ignoradas: {len(ignorados)}\n")
    
    if ignorados:
        print(f"=== DETALHES DOS IGNORADOS ({len(ignorados)}) ===")
        for linha, motivo, row in ignorados[:50]:
            print(f"Linha {linha}: {motivo}")
            print(f"  Dados: {row[:8]}")
            print()
    
    conn.close()

if __name__ == "__main__":
    analisar_e_corrigir()
