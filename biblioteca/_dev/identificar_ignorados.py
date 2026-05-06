import sqlite3
import csv
import io
import sys

def analyze_csv(csv_path):
    db_path = 'instance/biblioteca.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get existing patrimonies
    c.execute("SELECT patrimony FROM books")
    existing = set(row[0] for row in c.fetchall())
    
    print(f"Analisando: {csv_path}\n")
    print(f"Livros já cadastrados no banco: {len(existing)}\n")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        reader = csv.DictReader(io.StringIO(content))
        
        vazios = []
        duplicados_banco = []
        duplicados_csv = {}
        erros = []
        patrimonies_no_csv = {}
        
        for i, row in enumerate(reader, 1):
            pat = (row.get('patrimonio') or row.get('patrimônio') or row.get('PAT') or '').strip().upper()
            title = (row.get('titulo') or row.get('título') or row.get('title') or '').strip()
            
            # Check empty
            if not pat or not title:
                vazios.append((i, pat, title))
                continue
            
            # Check duplicates in CSV
            if pat in patrimonies_no_csv:
                if pat not in duplicados_csv:
                    duplicados_csv[pat] = [patrimonies_no_csv[pat]]
                duplicados_csv[pat].append(i)
                continue
            
            patrimonies_no_csv[pat] = i
            
            # Check if exists in database
            if pat in existing:
                duplicados_banco.append((i, pat, title))
        
        # Print results
        print("=" * 60)
        print("RELATÓRIO DE ITENS QUE SERIAM IGNORADOS")
        print("=" * 60)
        
        print(f"\n1. PATRIMÔNIO OU TÍTULO VAZIO: {len(vazios)}")
        for linha, pat, titulo in vazios[:10]:
            print(f"   Linha {linha}: PAT='{pat}', Título='{titulo}'")
        if len(vazios) > 10:
            print(f"   ... e mais {len(vazios) - 10} itens")
        
        print(f"\n2. PATRIMÔNIO JÁ EXISTE NO BANCO: {len(duplicados_banco)}")
        for linha, pat, titulo in duplicados_banco[:10]:
            print(f"   Linha {linha}: PAT={pat}, Título='{titulo}'")
        if len(duplicados_banco) > 10:
            print(f"   ... e mais {len(duplicados_banco) - 10} itens")
        
        print(f"\n3. PATRIMÔNIO DUPLICADO NO CSV: {len(duplicados_csv)}")
        for pat, linhas in list(duplicados_csv.items())[:10]:
            print(f"   PAT {pat}: linhas {linhas}")
        if len(duplicados_csv) > 10:
            print(f"   ... e mais {len(duplicados_csv) - 10} itens")
        
        total_ignorados = len(vazios) + len(duplicados_banco) + len(duplicados_csv)
        print(f"\n" + "=" * 60)
        print(f"TOTAL DE ITENS QUE SERIAM IGNORADOS: {total_ignorados}")
        print("=" * 60)
        
        # Export to file
        with open('analise_importacao.txt', 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE ANÁLISE DE IMPORTAÇÃO CSV\n\n")
            f.write(f"Arquivo: {csv_path}\n")
            f.write(f"Livros no banco: {len(existing)}\n\n")
            f.write(f"Itens vazios: {len(vazios)}\n")
            for linha, pat, titulo in vazios:
                f.write(f"  Linha {linha}: PAT='{pat}', Título='{titulo}'\n")
            f.write(f"\nItens já no banco: {len(duplicados_banco)}\n")
            for linha, pat, titulo in duplicados_banco:
                f.write(f"  Linha {linha}: PAT={pat}, Título='{titulo}'\n")
            f.write(f"\nItens duplicados no CSV: {len(duplicados_csv)}\n")
            for pat, linhas in duplicados_csv.items():
                f.write(f"  PAT {pat}: linhas {linhas}\n")
        
        print(f"\nRelatório completo salvo em: analise_importacao.txt")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_path}' não encontrado.")
        print("Uso: python identificar_ignorados.py <arquivo.csv>")
    except Exception as e:
        print(f"Erro: {e}")
    
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        analyze_csv(sys.argv[1])
    else:
        print("Uso: python identificar_ignorados.py <arquivo.csv>")
        print("\nArquivos CSV encontrados:")
        import glob
        for f in glob.glob("*.csv"):
            print(f"  - {f}")
