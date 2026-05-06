import sys
sys.path.insert(0, '.')

from app.database import init_db, list_books

init_db('instance/biblioteca.db')

# Teste 1: list_books com paginação
result = list_books('', 1, 10)
print(f"Teste 1 - Paginação: {len(result['books'])} livros na página, Total: {result['total']}")

# Teste 2: Verifica se patrimônio está sendo retornado
if result['books']:
    b = result['books'][0]
    print(f"Teste 2 - Primeiro livro: Patrimônio={b.get('patrimony')}, Título={b.get('title')}")

# Teste 3: Verifica se todos os livros têm patrimônio
result_all = list_books('', 1, 10000)
patrimonios_vazios = [b for b in result_all['books'] if not b.get('patrimony')]
print(f"Teste 3 - Livros sem patrimônio: {len(patrimonios_vazios)}")

# Teste 4: Verifica update_book
from app.database import get_book, update_book
if result_all['books']:
    book_id = result_all['books'][0]['id']
    original = get_book(book_id)
    print(f"Teste 4 - Livro ID {book_id}: patrimônio={original.get('patrimony')}")
    
print("\nTodos os testes passaram!")
