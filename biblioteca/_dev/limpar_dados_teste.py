"""
LIMPEZA DE DADOS DE TESTE - Biblioteca Sistema
Selecione quais dados devem ser apagados do banco.
Mantem: usuarios, instituicao, licenca, permissoes
"""
import sys
import os
import shutil
import sqlite3
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TABLES_INFO = {
    'books':       ('Livros (acervo)', True),
    'students':    ('Alunos', True),
    'loans':       ('Emprestimos', True),
    'activity_log':('Log de atividades', True),
    'categories':  ('Categorias', False),
}

BANNER = """
================================================
   LIMPEZA DE DADOS DE TESTE - Biblioteca
================================================
"""

def find_database():
    candidates = [
        os.path.join(SCRIPT_DIR, "instance", "biblioteca.db"),
        os.path.join(SCRIPT_DIR, "..", "instance", "biblioteca.db"),
        os.path.join("instance", "biblioteca.db"),
        "biblioteca.db",
    ]
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.exists(path):
            return path
    return None


def check_port_in_use(port=5477):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def make_backup(db_path):
    backup_dir = os.path.normpath(os.path.join(os.path.dirname(db_path), "..", "backups"))
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_antes_limpeza_{ts}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def get_count(conn, table):
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except Exception:
        return "N/A"


def select_tables():
    print("Selecione o que deve ser APAGADO do banco:\n")
    selected = []
    for i, (table, (desc, default)) in enumerate(TABLES_INFO.items(), 1):
        default_str = "(padrao)" if default else "(opcional)"
        choice = input(f"  {i}. {desc} {default_str}? [{'S/n' if default else 's/N'}]: ").strip().lower()
        if default:
            if choice != 'n':
                selected.append(table)
        else:
            if choice == 's':
                selected.append(table)
    return selected


def clean(db_path, tables):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        for table in tables:
            try:
                deleted = conn.execute(f"DELETE FROM {table}").rowcount
                print(f"  [OK] {table}: {deleted} registro(s) removido(s)")
            except sqlite3.OperationalError as e:
                print(f"  [AV] {table}: {e}")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        conn.execute("VACUUM")
        print()
        print("  Verificacao apos limpeza:")
        for table in ['books', 'students', 'loans', 'activity_log', 'categories']:
            try:
                print(f"    {table:20}: {get_count(conn, table)}")
            except Exception:
                pass
    finally:
        conn.close()


def main():
    print(BANNER)

    if check_port_in_use(5477):
        print("[ERRO] O sistema Biblioteca esta rodando!")
        print("       Encerre o sistema antes de continuar.\n")
        input("Pressione Enter para sair...")
        sys.exit(1)

    db_path = find_database()
    if not db_path:
        print("[ERRO] Banco de dados nao encontrado!")
        print("       Esperado em: instance\\biblioteca.db\n")
        input("Pressione Enter para sair...")
        sys.exit(1)

    print(f"[OK] Banco encontrado: {db_path}")
    size_mb = os.path.getsize(db_path) / 1024 / 1024
    print(f"     Tamanho: {size_mb:.2f} MB\n")

    tables = select_tables()
    if not tables:
        print("\n  Nenhum dado selecionado. Operacao cancelada.\n")
        input("Pressione Enter para sair...")
        sys.exit(0)

    print(f"\n  Serao apagados: {', '.join(tables)}")
    confirm = input("\n  Tem certeza? Digite SIM para continuar: ").strip()
    if confirm.upper() != "SIM":
        print("\n  Operacao cancelada.\n")
        input("Pressione Enter para sair...")
        sys.exit(0)

    print("\n[..] Criando backup...")
    try:
        backup_path = make_backup(db_path)
        print(f"[OK] Backup: {backup_path}\n")
    except Exception as e:
        print(f"[ERRO] Falha ao criar backup: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)

    print("[..] Limpando dados de teste...\n")
    try:
        clean(db_path, tables)
    except Exception as e:
        print(f"\n[ERRO] Falha na limpeza: {e}")
        print(f"       Restaure o backup em: {backup_path}")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    print("\n================================================")
    print("  LIMPEZA CONCLUIDA COM SUCESSO!")
    print("  O sistema esta pronto para uso em producao.")
    print("================================================\n")
    input("Pressione Enter para sair...")


if __name__ == "__main__":
    main()
