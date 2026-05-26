import sqlite3
import os

db_path = "biblioteca.db"
if not os.path.exists(db_path):
    print(f"Banco nao encontrado: {db_path}")
    exit()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tabelas no banco:")
    for t in tables:
        print(f"  - {t[0]}")
    
    # Verificar se as tabelas essenciais existem
    expected = ['institution', 'users', 'books', 'students', 'loans', 'activity_log']
    existing = [t[0] for t in tables]
    for e in expected:
        if e not in existing:
            print(f"  ERRO: Tabela '{e}' nao encontrada!")
    
    conn.close()
    print("Verificacao concluida.")
except Exception as ex:
    print(f"Erro: {ex}")
