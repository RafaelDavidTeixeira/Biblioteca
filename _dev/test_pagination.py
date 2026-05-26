from app.database import init_db, list_books
import os

# Initialize database
db_path = 'instance/biblioteca.db'
if os.path.exists(db_path):
    init_db(db_path)
    
    # Test pagination
    result = list_books('', 1, 50)
    print(f"Página 1: {len(result['books'])} livros retornados")
    print(f"Total: {result['total']}, Páginas: {result['pages']}")
    
    # Test with search
    result2 = list_books('harry', 1, 50)
    print(f"\nBusca 'harry': {len(result2['books'])} livros encontrados")
    print(f"Total: {result2['total']}")
else:
    print("Banco de dados não encontrado.")
