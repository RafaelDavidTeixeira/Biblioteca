import csv
import io

def validar_csv_livros(conteudo_csv):
    """
    Valida um arquivo CSV de livros simulando a lógica de importação.
    Retorna: (importados, ignorados, erros, detalhes_ignorados)
    """
    # Simular leitura do CSV
    reader = csv.DictReader(io.StringIO(conteudo_csv))
    
    linhas_processadas = []
    ignorados = []
    erros = []
    
    # Simular patrimônios já existentes (vazia para validação inicial)
    patrimonios_existentes = set()
    
    for i, row in enumerate(reader, 1):
        try:
            # Extrair campos como no código original
            pat = (row.get('patrimonio') or row.get('patrimônio') or row.get('PAT') or '').strip().upper()
            title = (row.get('titulo') or row.get('título') or row.get('title') or '').strip()
            
            # Verificar campos obrigatórios
            if not pat and not title:
                ignorados.append({
                    'linha': i+1,
                    'motivo': 'patrimônio e título vazios',
                    'dados': row
                })
                continue
            elif not pat:
                ignorados.append({
                    'linha': i+1,
                    'motivo': 'patrimônio vazio',
                    'dados': row
                })
                continue
            elif not title:
                ignorados.append({
                    'linha': i+1,
                    'motivo': 'título vazio',
                    'dados': row
                })
                continue
            
            # Verificar duplicatas
            if pat in patrimonios_existentes:
                ignorados.append({
                    'linha': i+1,
                    'motivo': f'patrimônio {pat} já existe',
                    'dados': row
                })
                continue
            
            # Simular importação bem-sucedida
            patrimonios_existentes.add(pat)
            linhas_processadas.append({
                'linha': i+1,
                'patrimonio': pat,
                'titulo': title,
                'autor': (row.get('autor') or row.get('author') or '').strip(),
                'isbn': (row.get('isbn') or '').strip(),
                'categoria': (row.get('categoria') or row.get('category') or '').strip(),
                'editora': (row.get('editora') or row.get('publisher') or '').strip()
            })
            
        except Exception as e:
            erros.append(f'Linha {i+1}: {e}')
    
    return linhas_processadas, ignorados, erros

# Exemplo de uso (quando o usuário enviar o CSV):
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        arquivo = sys.argv[1]
        print(f"Validando arquivo: {arquivo}")
        
        try:
            with open(arquivo, 'r', encoding='utf-8-sig') as f:
                conteudo = f.read()
            
            processados, ignorados, erros = validar_csv_livros(conteudo)
            
            print(f"\n=== RESULTADO ===")
            print(f"Linhas processadas com sucesso: {len(processados)}")
            print(f"Linhas ignoradas: {len(ignorados)}")
            print(f"Erros: {len(erros)}")
            
            if ignorados:
                print(f"\n=== DETALHES DOS IGNORADOS ({len(ignorados)}) ===")
                for item in ignorados[:20]:  # Mostrar apenas os primeiros 20
                    print(f"Linha {item['linha']}: {item['motivo']}")
                    print(f"  Dados: {item['dados']}")
                    print()
            
            if erros:
                print(f"\n=== ERROS ===")
                for erro in erros[:10]:
                    print(erro)
                    
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {arquivo}")
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
    else:
        print("Uso: python validar_csv.py arquivo.csv")
        print("Exemplo: python validar_csv.py livros.csv")
