import sqlite3

db_path = 'instance/biblioteca.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# List all tables
print("=== TABELAS NO BANCO ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for t in tables:
    print(f"  - {t[0]}")

# Check activity_log table
print("\n=== LOGS DE IMPORTAÇÃO ===")
try:
    c.execute("SELECT * FROM activity_log WHERE type='import_books' ORDER BY id DESC LIMIT 10")
    logs = c.fetchall()
    if logs:
        for log in logs:
            print(f"ID: {log[0]}, Tipo: {log[1]}, Descrição: {log[2]}, Data: {log[4]}")
    else:
        print("Nenhum log de importação encontrado.")
except sqlite3.OperationalError as e:
    print(f"Erro: {e}")

conn.close()
