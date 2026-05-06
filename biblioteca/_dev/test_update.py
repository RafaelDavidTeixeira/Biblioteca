import sqlite3

db_path = 'instance/biblioteca.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check current enrollment for student ID 1589
c.execute("SELECT id, name, enrollment FROM students WHERE id=?", (1589,))
row = c.fetchone()
print(f"Antes: ID={row[0]}, Nome={row[1]}, Matrícula={row[2]}")

# Try direct update
new_enrollment = "1C-01_TEST"
c.execute("UPDATE students SET enrollment=? WHERE id=?", (new_enrollment, 1589))
conn.commit()
print(f"Update executado. Linhas afetadas: {c.rowcount}")

# Check if it worked
c.execute("SELECT id, name, enrollment FROM students WHERE id=?", (1589,))
row = c.fetchone()
print(f"Após update direto: ID={row[0]}, Nome={row[1]}, Matrícula={row[2]}")

# Revert
c.execute("UPDATE students SET enrollment=? WHERE id=?", ("1C-01", 1589))
conn.commit()
c.execute("SELECT id, name, enrollment FROM students WHERE id=?", (1589,))
row = c.fetchone()
print(f"Revertido: ID={row[0]}, Nome={row[1]}, Matrícula={row[2]}")

conn.close()
