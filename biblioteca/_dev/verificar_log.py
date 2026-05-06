import sqlite3
import os

# Caminho correto do banco
db_path = os.path.join("instance", "biblioteca.db")
print(f"Verificando banco: {db_path}")
print(f"Arquivo existe: {os.path.exists(db_path)}\n")

if not os.path.exists(db_path):
    print("Banco de dados não encontrado!")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Verificar tabelas
print("=== TABELAS ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in c.fetchall():
    print(f"- {t['name']}")

# Log de importação
print("\n=== LOG DE IMPORTAÇÃO ===")
try:
    c.execute("SELECT * FROM activity_log WHERE type='import_books' ORDER BY id DESC")
    logs = c.fetchall()
    if logs:
        for log in logs:
            print(f"{log['created_at']}: {log['description']}")
    else:
        print("Nenhum log encontrado")
except Exception as e:
    print(f"Erro: {e}")

# Total de livros
print("\n=== LIVROS ===")
c.execute("SELECT COUNT(*) as total FROM books")
print(f"Total: {c.fetchone()['total']}")

c.execute("SELECT COUNT(*) as total FROM books WHERE active=1")
print(f"Ativos: {c.fetchone()['total']}")

conn.close()
