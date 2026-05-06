import sqlite3

db_path = 'biblioteca.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Verificar log de importação de livros
print("=== LOG DE IMPORTAÇÃO DE LIVROS ===")
c.execute("SELECT * FROM activity_log WHERE type='import_books' ORDER BY id DESC LIMIT 10")
logs = c.fetchall()
for log in logs:
    print(f"ID: {log['id']}, Data: {log['created_at']}, Descrição: {log['description']}")

# Verificar total de livros importados
print("\n=== TOTAL DE LIVROS NO BANCO ===")
c.execute("SELECT COUNT(*) as total FROM books WHERE active=1")
total = c.fetchone()['total']
print(f"Total de livros ativos: {total}")

# Verificar livros por patrimônio duplicado ou vazio
print("\n=== VERIFICAR PROBLEMAS NOS LIVROS ===")
c.execute("SELECT COUNT(*) as total FROM books WHERE patrimony IS NULL OR patrimony=''")
sem_patrimonio = c.fetchone()['total']
print(f"Livros sem patrimônio: {sem_patrimonio}")

c.execute("SELECT COUNT(*) as total FROM books WHERE title IS NULL OR title=''")
sem_titulo = c.fetchone()['total']
print(f"Livros sem título: {sem_titulo}")

conn.close()
