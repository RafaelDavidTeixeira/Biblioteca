import sqlite3

conn = sqlite3.connect('instance/biblioteca.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM books WHERE active=1")
print("Livros ativos:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM books WHERE active=0")
print("Livros inativos:", c.fetchone()[0])

c.execute("SELECT description FROM activity_log WHERE type='import_books' ORDER BY id DESC LIMIT 1")
row = c.fetchone()
print("Último log de importação:", row[0] if row else "Nenhum")

c.execute("SELECT id, patrimony, title FROM books WHERE active=1 LIMIT 5")
rows = c.fetchall()
print("\nPrimeiros 5 livros ativos:")
for r in rows:
    print(f"  ID={r['id']}, Patrimônio={r['patrimony']}, Título={r['title']}")

conn.close()
