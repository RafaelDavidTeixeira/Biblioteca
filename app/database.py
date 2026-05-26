"""
Database layer using pure sqlite3 (Python stdlib).
No SQLAlchemy needed — zero external dependencies beyond Flask.
"""
import sqlite3
import os
import contextlib
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

_db_path = None


SCHEMA_VERSION = 6

def init_db(db_path: str):
    global _db_path
    _db_path = db_path
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    _create_tables()
    _seed_defaults()
    _run_migrations()


def _get_schema_version():
    with get_conn() as c:
        try:
            r = c.execute("SELECT version FROM db_version LIMIT 1").fetchone()
            return r[0] if r else 0
        except:
            return 0


def _set_schema_version(version):
    with get_conn() as c:
        try:
            c.execute("CREATE TABLE IF NOT EXISTS db_version (version INTEGER PRIMARY KEY, updated_at TEXT)")
            c.execute("INSERT OR REPLACE INTO db_version (version, updated_at) VALUES (?, ?)",
                      (version, datetime.now().isoformat()))
            c.commit()
        except:
            pass


def _run_migrations():
    current = _get_schema_version()
    if current >= SCHEMA_VERSION:
        return

    with get_conn() as c:
        if current < 2:
            cols = [r[1] for r in c.execute("PRAGMA table_info(institution)").fetchall()]
            if 'logo_path' not in cols:
                c.execute("ALTER TABLE institution ADD COLUMN logo_path TEXT DEFAULT ''")
            cols_b = [r[1] for r in c.execute("PRAGMA table_info(books)").fetchall()]
            if 'quantity' not in cols_b:
                c.execute("ALTER TABLE books ADD COLUMN quantity INTEGER DEFAULT 1")
            if 'location' not in cols_b:
                c.execute("ALTER TABLE books ADD COLUMN location TEXT DEFAULT ''")
            cols_p = [r[1] for r in c.execute("PRAGMA table_info(operator_permissions)").fetchall()]
            if 'can_view_activity' not in cols_p:
                c.execute("ALTER TABLE operator_permissions ADD COLUMN can_view_activity INTEGER DEFAULT 1")

        if current < 3:
            cols = [r[1] for r in c.execute("PRAGMA table_info(loans)").fetchall()]
            if 'renewed' not in cols:
                c.execute("ALTER TABLE loans ADD COLUMN renewed INTEGER DEFAULT 0")
            if 'renewed_at' not in cols:
                c.execute("ALTER TABLE loans ADD COLUMN renewed_at TEXT")

        if current < 4:
            tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if 'reservations' not in tables:
                c.execute("""CREATE TABLE reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL REFERENCES books(id),
                    student_id INTEGER NOT NULL REFERENCES students(id),
                    user_id INTEGER REFERENCES users(id),
                    reserved_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    notes TEXT DEFAULT ''
                )""")

        if current < 5:
            op_cols = [r[1] for r in c.execute("PRAGMA table_info(operator_permissions)").fetchall()]
            if 'can_renew_loans' not in op_cols:
                c.execute("ALTER TABLE operator_permissions ADD COLUMN can_renew_loans INTEGER DEFAULT 1")
            if 'can_manage_reservations' not in op_cols:
                c.execute("ALTER TABLE operator_permissions ADD COLUMN can_manage_reservations INTEGER DEFAULT 1")

        if current < 6:
            cols = [r[1] for r in c.execute("PRAGMA table_info(institution)").fetchall()]
            if 'desenvolvido_por' not in cols:
                c.execute("ALTER TABLE institution ADD COLUMN desenvolvido_por TEXT DEFAULT 'Sua equipe'")

        c.commit()
        _set_schema_version(SCHEMA_VERSION)


@contextlib.contextmanager
def get_conn():
    import time
    max_retries = 5
    conn = None
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(_db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                conn.execute("PRAGMA journal_mode = WAL")
            except:
                pass
            break
        except sqlite3.OperationalError as e:
            if conn:
                conn.close()
                conn = None
            if 'locked' in str(e).lower() and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise
    if conn is None:
        raise sqlite3.OperationalError("Banco de dados bloqueado após múltiplas tentativas")
    try:
        yield conn
    finally:
        if conn:
            conn.close()


def _create_tables():
    with get_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS institution (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL DEFAULT 'Minha Escola',
            cnpj TEXT DEFAULT '',
            address TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            loan_days_default INTEGER DEFAULT 14,
            logo_path TEXT DEFAULT '',
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'operator',
            active INTEGER DEFAULT 1,
            created_at TEXT,
            last_login TEXT
        );
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patrimony TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT DEFAULT '',
            isbn TEXT DEFAULT '',
            category TEXT DEFAULT '',
            publisher TEXT DEFAULT '',
            year INTEGER,
            location TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            quantity INTEGER DEFAULT 1,
            active INTEGER DEFAULT 1,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            enrollment TEXT UNIQUE NOT NULL,
            class_name TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT
        );
         CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id),
            student_id INTEGER NOT NULL REFERENCES students(id),
            user_id INTEGER REFERENCES users(id),
            borrowed_at TEXT NOT NULL,
            due_date TEXT NOT NULL,
            returned INTEGER DEFAULT 0,
            returned_at TEXT,
            renewed INTEGER DEFAULT 0,
            renewed_at TEXT,
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id),
            student_id INTEGER NOT NULL REFERENCES students(id),
            user_id INTEGER REFERENCES users(id),
            reserved_at TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            description TEXT,
            user_id INTEGER REFERENCES users(id),
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS license_info (
            id INTEGER PRIMARY KEY,
            machine_id TEXT,
            license_key TEXT,
            institution_name TEXT,
            valid_until TEXT,
            activated_at TEXT,
            is_valid INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS operator_permissions (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            can_create_books INTEGER DEFAULT 1,
            can_edit_books INTEGER DEFAULT 1,
            can_delete_books INTEGER DEFAULT 0,
            can_create_students INTEGER DEFAULT 1,
            can_edit_students INTEGER DEFAULT 1,
            can_delete_students INTEGER DEFAULT 0,
            can_create_loans INTEGER DEFAULT 1,
            can_return_books INTEGER DEFAULT 1,
            can_renew_loans INTEGER DEFAULT 1,
            can_manage_reservations INTEGER DEFAULT 1,
            can_view_reports INTEGER DEFAULT 1,
            can_print_barcodes INTEGER DEFAULT 1,
            can_manage_categories INTEGER DEFAULT 0,
            can_backup INTEGER DEFAULT 0,
            can_view_activity INTEGER DEFAULT 1,
            updated_at TEXT
        );
        
        -- FTS5 para busca rápida e inteligente
        CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(title, author, patrimony, isbn, content='books', content_rowid='id', tokenize='unicode61 remove_diacritics 1');
        CREATE VIRTUAL TABLE IF NOT EXISTS students_fts USING fts5(name, enrollment, class_name, content='students', content_rowid='id', tokenize='unicode61 remove_diacritics 1');
        
        -- Triggers para manter FTS sincronizado (Books)
        CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books BEGIN INSERT INTO books_fts(rowid, title, author, patrimony, isbn) VALUES (new.id, new.title, new.author, new.patrimony, new.isbn); END;
        CREATE TRIGGER IF NOT EXISTS books_ad AFTER DELETE ON books BEGIN INSERT INTO books_fts(books_fts, rowid, title, author, patrimony, isbn) VALUES('delete', old.id, old.title, old.author, old.patrimony, old.isbn); END;
        CREATE TRIGGER IF NOT EXISTS books_au AFTER UPDATE ON books BEGIN INSERT INTO books_fts(books_fts, rowid, title, author, patrimony, isbn) VALUES('delete', old.id, old.title, old.author, old.patrimony, old.isbn); INSERT INTO books_fts(rowid, title, author, patrimony, isbn) VALUES (new.id, new.title, new.author, new.patrimony, new.isbn); END;
        
        -- Triggers para manter FTS sincronizado (Students)
        CREATE TRIGGER IF NOT EXISTS students_ai AFTER INSERT ON students BEGIN INSERT INTO students_fts(rowid, name, enrollment, class_name) VALUES (new.id, new.name, new.enrollment, new.class_name); END;
        CREATE TRIGGER IF NOT EXISTS students_ad AFTER DELETE ON students BEGIN INSERT INTO students_fts(students_fts, rowid, name, enrollment, class_name) VALUES('delete', old.id, old.name, old.enrollment, old.class_name); END;
        CREATE TRIGGER IF NOT EXISTS students_au AFTER UPDATE ON students BEGIN INSERT INTO students_fts(students_fts, rowid, name, enrollment, class_name) VALUES('delete', old.id, old.name, old.enrollment, old.class_name); INSERT INTO students_fts(rowid, name, enrollment, class_name) VALUES (new.id, new.name, new.enrollment, new.class_name); END;
        """)
    _rebuild_fts()


def _seed_defaults():
    with get_conn() as conn:
        # Apenas criar usuário admin para primeira configuração
        if not conn.execute("SELECT 1 FROM users WHERE email=?", ('admin@biblioteca.local',)).fetchone():
            conn.execute("""INSERT INTO users (name, email, password_hash, role, active, created_at)
                         VALUES (?,?,?,?,?,?)""",
                      ('Administrador', 'admin@biblioteca.local',
                       generate_password_hash('admin123'), 'admin', 1, _now()))
        # Garantir que linha da instituição existe (UPDATE precisa dela)
        if not conn.execute("SELECT 1 FROM institution WHERE id=1").fetchone():
            conn.execute("INSERT INTO institution (id, name, loan_days_default) VALUES (1, 'Minha Escola', 14)")
        # Criar categorias padrão se não existirem
        default_cats = [
            'Administração', 'Antropologia', 'Arqueologia', 'Arquitetura e Urbanismo',
            'Arte', 'Astronomia', 'Biblioteconomia e Ciência da Informação', 'Bioética',
            'Biologia', 'Ciências Contábeis', 'Ciências Políticas', 'Comunicação Social',
            'Contos', 'Direito', 'Economia', 'Educação Física', 'Enfermagem',
            'Engenharia Ambiental', 'Engenharia Civil', 'Engenharia de Produção',
            'Engenharia Elétrica', 'Engenharia Mecânica', 'Engenharia Química',
            'Filosofia', 'Física', 'Fonoaudiologia', 'Geografia', 'Geologia',
            'Gestão de Pessoas', 'História', 'História em Quadrinhos', 'Informática',
            'Inglês', 'Literatura Brasileira', 'Literatura Estrangeira',
            'Literatura Infantojuvenil', 'Logística', 'Marketing', 'Matemática',
            'Medicina', 'Medicina Veterinária', 'Meio Ambiente', 'Música', 'Nutrição',
            'Odontologia', 'Pedagogia', 'Poesia', 'Psicologia', 'Química', 'Religião',
            'Saúde Coletiva', 'Serviço Social', 'Sociologia', 'Teatro', 'Turismo'
        ]
        for cat in default_cats:
            if not conn.execute("SELECT 1 FROM categories WHERE name=?", (cat,)).fetchone():
                conn.execute("INSERT INTO categories (name, active) VALUES (?, 1)", (cat,))
        conn.commit()

def _rebuild_fts():
    """Garante que a tabela FTS está populada (para migrações ou bancos existentes)."""
    try:
        with get_conn() as c:
            c.execute("INSERT OR REPLACE INTO books_fts(rowid, title, author, patrimony, isbn) SELECT id, title, author, patrimony, isbn FROM books")
            c.execute("INSERT OR REPLACE INTO students_fts(rowid, name, enrollment, class_name) SELECT id, name, enrollment, class_name FROM students")
            c.commit()
    except Exception:
        pass # Ignora se FTS não existir ainda


def _now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _today():
    return date.today().isoformat()

def _fmt_date(s):
    if not s: return ''
    try: return datetime.fromisoformat(s[:10]).strftime('%d/%m/%Y')
    except: return s

def _fmt_dt(s):
    if not s: return ''
    try: return datetime.fromisoformat(s).strftime('%d/%m/%Y %H:%M')
    except: return s

def _row(r):
    return dict(r) if r else None

def log_activity(type_, description, user_id=None):
    with get_conn() as c:
        c.execute("INSERT INTO activity_log (type,description,user_id,created_at) VALUES(?,?,?,?)",
                  (type_, description, user_id, _now()))
        c.commit()

# ── INSTITUTION ────────────────────────────────────────────────
def get_institution():
    with get_conn() as c:
        result = _row(c.execute("SELECT * FROM institution LIMIT 1").fetchone())
        c.commit()
        return result

def update_institution(data):
    with get_conn() as conn:
        # Garante que a linha existe antes de atualizar
        if not conn.execute("SELECT 1 FROM institution WHERE id=1").fetchone():
            conn.execute("INSERT INTO institution (id, name, loan_days_default) VALUES (1, 'Minha Escola', 14)")
        conn.execute("""UPDATE institution SET name=?,cnpj=?,address=?,phone=?,email=?,
                     loan_days_default=?,updated_at=? WHERE id=1""",
                  (data.get('name',''), data.get('cnpj',''), data.get('address',''),
                   data.get('phone',''), data.get('email',''),
                   int(data.get('loan_days_default',14)), _now()))
        conn.commit()

def update_institution_logo(logo_path):
    with get_conn() as conn:
        conn.execute("UPDATE institution SET logo_path=?,updated_at=? WHERE id=1", (logo_path, _now()))
        conn.commit()

# ── USERS ──────────────────────────────────────────────────────
def _user_dict(r):
    if not r: return None
    d = dict(r)
    d['created_at'] = _fmt_dt(d.get('created_at',''))
    d['last_login'] = _fmt_dt(d.get('last_login','')) or 'Nunca'
    return d

def get_user_by_email(email):
    with get_conn() as c:
        result = _row(c.execute("SELECT * FROM users WHERE email=? AND active=1",(email,)).fetchone())
        c.commit()
        return result

def get_user_by_login_identifier(identifier):
    with get_conn() as c:
        result = _row(c.execute(
            "SELECT * FROM users WHERE (email=? OR name=? OR email LIKE ?) AND active=1 LIMIT 1",
            (identifier, identifier, f'%{identifier}%')
        ).fetchone())
        c.commit()
        return result
        c.commit()

def get_user_by_id(uid):
    with get_conn() as c:
        result = _row(c.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
        c.commit()
        return result
        c.commit()

def list_users():
    with get_conn() as c:
        users = [_user_dict(r) for r in c.execute("SELECT * FROM users ORDER BY name").fetchall()]
        c.commit()
        return users

def create_user(data):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO users (name,email,password_hash,role,active,created_at) VALUES(?,?,?,?,1,?)",
                  (data['name'], data['email'], generate_password_hash(data['password']),
                   data.get('role','operator'), _now()))
        lid = cur.lastrowid; conn.commit()
    # Buscar usuário recém-criado com nova conexão
    with get_conn() as c:
        result = _user_dict(_row(c.execute("SELECT * FROM users WHERE id=?",(lid,)).fetchone()))
        c.commit()
        return result

def update_user(uid, data):
    with get_conn() as conn:
        if data.get('password'):
            conn.execute("UPDATE users SET name=?,role=?,active=?,password_hash=? WHERE id=?",
                      (data['name'], data.get('role','operator'), int(data.get('active',1)),
                       generate_password_hash(data['password']), uid))
        else:
            conn.execute("UPDATE users SET name=?,role=?,active=? WHERE id=?",
                      (data['name'], data.get('role','operator'), int(data.get('active',1)), uid))
        conn.commit()

def deactivate_user(uid):
    with get_conn() as conn:
        conn.execute("UPDATE users SET active=0 WHERE id=?",(uid,))
        conn.commit()

def update_last_login(uid):
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_login=? WHERE id=?",(_now(), uid))
        conn.commit()

def check_user_password(uid, password):
    with get_conn() as c:
        r = c.execute("SELECT password_hash FROM users WHERE id=?",(uid,)).fetchone()
        return check_password_hash(r['password_hash'], password) if r else False
        c.commit()

def change_user_password(uid, new_password):
    with get_conn() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE id=?",(generate_password_hash(new_password), uid))
        conn.commit()

# ── BOOKS ──────────────────────────────────────────────────────
def _book_is_available(book_id):
    with get_conn() as c:
        return c.execute("SELECT 1 FROM loans WHERE book_id=? AND returned=0 LIMIT 1",(book_id,)).fetchone() is None
        c.commit()

def _book_active_loans_count(book_id):
    with get_conn() as c:
        return c.execute("SELECT COUNT(*) FROM loans WHERE book_id=? AND returned=0",(book_id,)).fetchone()[0]
        c.commit()

def _book_dict(r):
    if not r: return None
    d = dict(r)
    d['created_at'] = _fmt_dt(d.get('created_at',''))
    # Usar quantity do banco se existir, senão padrão 1
    d['quantity'] = d.get('quantity', 1) or 1
    d['available_qty'] = d['quantity'] if d.get('available', True) else 0
    d['location'] = d.get('location', '')
    return d

def list_books(q='', page=1, per_page=50, sort_by='title', sort_order='asc'):
    sort_order = 'ASC' if sort_order == 'asc' else 'DESC'
    try:
        with get_conn() as c:
            if q:
                lk = f'%{q}%'
                where = "WHERE active=1 AND (title LIKE ? OR author LIKE ? OR patrimony LIKE ? OR isbn LIKE ?)"
                params = [lk, lk, lk, lk]
                if sort_by == 'patrimony':
                    order_clause = f"ORDER BY CAST(b.patrimony AS INTEGER) {sort_order}, b.id"
                else:
                    order_clause = "ORDER BY CASE WHEN b.title LIKE ? THEN 0 ELSE 1 END, b.title COLLATE NOCASE ASC, b.id"
                    params.append(q + '%')
            else:
                where = "WHERE active=1"
                params = ()
                if sort_by == 'patrimony':
                    order_clause = f"ORDER BY CAST(b.patrimony AS INTEGER) {sort_order}, b.id"
                else:
                    order_clause = "ORDER BY b.title COLLATE NOCASE ASC, b.id"

            query = f"""SELECT b.*,
                CASE WHEN l.id IS NOT NULL THEN 0 ELSE 1 END as available
                FROM books b
                LEFT JOIN loans l ON b.id = l.book_id AND l.returned=0
                {where}
                {order_clause}"""
            rows = c.execute(query, params).fetchall()
            books = [_book_dict(r) for r in rows]
            return {'books': books, 'total': len(books), 'page': 1, 'per_page': len(books), 'pages': 1}
            c.commit()
    except Exception as e:
        import logging
        logging.error(f"Erro em list_books: {e}", exc_info=True)
        return {'books': [], 'total': 0, 'page': 1, 'per_page': 50, 'pages': 0}

def search_books(q='', limit=50, sort_by='title', sort_order='asc'):
    """Busca simples por LIKE - usada no modal de empréstimos"""
    sort_order = 'ASC' if sort_order == 'asc' else 'DESC'
    if sort_by == 'patrimony':
        order_clause = f"ORDER BY CAST(b.patrimony AS INTEGER) {sort_order}, b.id"
    else:
        sort_by = sort_by if sort_by in ('title',) else 'title'
        order_clause = f"ORDER BY b.{sort_by} COLLATE NOCASE {sort_order}, b.id"
    try:
        with get_conn() as c:
            lk = f'%{q}%'
            sql = f"""SELECT b.*,
                CASE WHEN l.id IS NOT NULL THEN 0 ELSE 1 END as available
                FROM books b
                LEFT JOIN loans l ON b.id = l.book_id AND l.returned=0
                WHERE b.active=1 AND (b.title LIKE ? OR b.author LIKE ? OR b.patrimony LIKE ? OR b.isbn LIKE ?)
                {order_clause}
                LIMIT ?"""
            rows = c.execute(sql, (lk, lk, lk, lk, limit)).fetchall()
            return [_book_dict(r) for r in rows]
    except Exception as e:
        import logging
        logging.error(f"Erro em search_books: {e}", exc_info=True)
        return []

def get_book(book_id):
    with get_conn() as c:
        row = c.execute("""SELECT b.*,
            CASE WHEN l.id IS NOT NULL THEN 0 ELSE 1 END as available
            FROM books b
            LEFT JOIN loans l ON b.id = l.book_id AND l.returned=0
            WHERE b.id=?""",(book_id,)).fetchone()
        return _book_dict(row)
        c.commit()

def get_book_by_patrimony(patrimony):
    with get_conn() as c:
        row = c.execute("""SELECT b.*,
            CASE WHEN l.id IS NOT NULL THEN 0 ELSE 1 END as available
            FROM books b
            LEFT JOIN loans l ON b.id = l.book_id AND l.returned=0
            WHERE b.patrimony=?""",(patrimony,)).fetchone()
        return _book_dict(row)
        c.commit()

def create_book(data):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO books (patrimony,title,author,isbn,category,publisher,year,location,notes,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,1,?)",
                  (data['patrimony'].upper(), data['title'], data.get('author',''),
                   data.get('isbn',''), data.get('category',''), data.get('publisher',''),
                   data.get('year') or None, data.get('location',''), data.get('notes',''), _now()))
        lid = cur.lastrowid; conn.commit()
    return get_book(lid)

def update_book(book_id, data):
    with get_conn() as conn:
        c = conn.cursor()
        patrimony = data.get('patrimony', '').strip().upper()
        if patrimony:
            c.execute("UPDATE books SET patrimony=?,title=?,author=?,isbn=?,category=?,publisher=?,year=?,location=?,notes=? WHERE id=?",
                      (patrimony, data['title'], data.get('author',''), data.get('isbn',''),
                       data.get('category',''), data.get('publisher',''),
                       data.get('year') or None, data.get('location',''), data.get('notes',''), book_id))
        else:
            c.execute("UPDATE books SET title=?,author=?,isbn=?,category=?,publisher=?,year=?,location=?,notes=? WHERE id=?",
                      (data['title'], data.get('author',''), data.get('isbn',''),
                       data.get('category',''), data.get('publisher',''),
                       data.get('year') or None, data.get('location',''), data.get('notes',''), book_id))
        conn.commit()
    return get_book(book_id)

def deactivate_book(book_id):
    with get_conn() as conn:
        conn.execute("UPDATE books SET active=0 WHERE id=?",(book_id,))
        conn.commit()

# ── STUDENTS ───────────────────────────────────────────────────
_STUDENT_SELECT = """SELECT s.*,
    COALESCE(lcnt.active_loans, 0) as active_loans,
    CASE WHEN odcnt.overdue_count > 0 THEN 1 ELSE 0 END as has_overdue
    FROM students s
    LEFT JOIN (SELECT student_id, COUNT(*) as active_loans FROM loans WHERE returned=0 GROUP BY student_id) lcnt ON s.id = lcnt.student_id
    LEFT JOIN (SELECT student_id, COUNT(*) as overdue_count FROM loans WHERE returned=0 AND due_date < date('now') GROUP BY student_id) odcnt ON s.id = odcnt.student_id"""

def _student_dict(r):
    if not r: return None
    d = dict(r)
    d['created_at'] = _fmt_dt(d.get('created_at',''))
    return d

def list_students(q='', active_filter='active', sort_by='name', sort_order='asc'):
    sort_by = sort_by if sort_by in ('name', 'enrollment', 'class_name') else 'name'
    sort_order = 'ASC' if sort_order == 'asc' else 'DESC'
    with get_conn() as c:
        where = "WHERE 1=1"
        params = []
        if active_filter == 'active':
            where += " AND s.active=1"
        elif active_filter == 'inactive':
            where += " AND s.active=0"
        if q:
            lk = f'%{q}%'
            where += " AND (s.name LIKE ? OR s.enrollment LIKE ? OR s.class_name LIKE ?)"
            params.extend([lk, lk, lk])
        if q and sort_by == 'name':
            order = "ORDER BY CASE WHEN s.name LIKE ? THEN 0 ELSE 1 END, s.name COLLATE NOCASE ASC, s.id"
            params.append(q + '%')
        else:
            order = f"ORDER BY s.{sort_by} COLLATE NOCASE {sort_order}, s.id"
        rows = c.execute(f"{_STUDENT_SELECT} {where} {order}", params).fetchall()
        return [_student_dict(r) for r in rows]
        c.commit()

def get_student(sid):
    with get_conn() as c:
        return _student_dict(c.execute(_STUDENT_SELECT + " WHERE s.id=?",(sid,)).fetchone())
        c.commit()

def get_student_by_enrollment(enrollment):
    with get_conn() as c:
        return _student_dict(c.execute(_STUDENT_SELECT + " WHERE s.enrollment=? AND s.active=1",(enrollment,)).fetchone())
        c.commit()

def create_student(data):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO students (name,enrollment,class_name,phone,email,notes,active,created_at) VALUES(?,?,?,?,?,?,1,?)",
                  (data['name'], data['enrollment'], data.get('class_name',''),
                   data.get('phone',''), data.get('email',''), data.get('notes',''), _now()))
        lid = cur.lastrowid; conn.commit()
    return get_student(lid)

def update_student(sid, data):
    with get_conn() as conn:
        c = conn.cursor()
        enrollment = data.get('enrollment', '').strip()
        if enrollment:
            c.execute("UPDATE students SET name=?,enrollment=?,class_name=?,phone=?,email=?,notes=? WHERE id=?",
                      (data['name'], enrollment, data.get('class_name',''), data.get('phone',''),
                       data.get('email',''), data.get('notes',''), sid))
        else:
            c.execute("UPDATE students SET name=?,class_name=?,phone=?,email=?,notes=? WHERE id=?",
                      (data['name'], data.get('class_name',''), data.get('phone',''),
                       data.get('email',''), data.get('notes',''), sid))
        conn.commit()
    return get_student(sid)

def deactivate_student(sid):
    with get_conn() as conn:
        conn.execute("UPDATE students SET active=0 WHERE id=?",(sid,))
        conn.commit()

def deactivate_class(class_name):
    with get_conn() as conn:
        cur = conn.execute("UPDATE students SET active=0 WHERE class_name=? AND active=1", (class_name,))
        conn.commit()
        return cur.rowcount

def batch_update_class(changes):
    """changes = [{'id': sid, 'class_name': str, 'inactive': bool}, ...]"""
    with get_conn() as conn:
        for item in changes:
            sid = item['id']
            new_class = (item.get('class_name') or '').strip()
            inactive = item.get('inactive', False)
            if inactive:
                if new_class:
                    conn.execute("UPDATE students SET class_name=?, active=0 WHERE id=?", (new_class, sid))
                else:
                    conn.execute("UPDATE students SET active=0 WHERE id=?", (sid,))
            elif new_class:
                conn.execute("UPDATE students SET class_name=? WHERE id=?", (new_class, sid))
        conn.commit()
        return len(changes)

def get_students_by_class(class_name):
    with get_conn() as c:
        rows = c.execute("SELECT id, name, enrollment, class_name FROM students WHERE class_name=? AND active=1 ORDER BY name", (class_name,)).fetchall()
        return [dict(r) for r in rows]

def set_student_active(sid, active):
    with get_conn() as conn:
        conn.execute("UPDATE students SET active=? WHERE id=?", (active, sid))
        conn.commit()

# ── LOANS ──────────────────────────────────────────────────────
def _process_row(r, today):
    d = dict(r)
    d['is_overdue'] = not d['returned'] and d.get('due_date','') < today
    d['days_overdue'] = 0
    if d['is_overdue']:
        try: d['days_overdue'] = (date.today() - date.fromisoformat(d['due_date'])).days
        except: pass
    d['borrowed_at'] = _fmt_dt(d.get('borrowed_at',''))
    d['returned_at'] = _fmt_dt(d.get('returned_at',''))
    d['renewed_at'] = _fmt_dt(d.get('renewed_at',''))
    d['due_date_iso'] = d.get('due_date','')
    d['due_date'] = _fmt_date(d.get('due_date',''))
    d['student_id'] = d.get('student_id')
    d['book_id'] = d.get('book_id')
    return d

_LOAN_SELECT = """SELECT l.*,
    b.title as book_title, b.patrimony as book_patrimony,
    s.name as student_name, s.enrollment as student_enrollment, s.class_name as student_class,
    u.name as operator,
    (SELECT COUNT(*) FROM reservations WHERE book_id = l.book_id AND status='active') as reservation_count
    FROM loans l
    JOIN books b ON l.book_id=b.id
    JOIN students s ON l.student_id=s.id
    LEFT JOIN users u ON l.user_id=u.id"""

def list_loans(status='active', q=''):
    today = _today()
    with get_conn() as c:
        sql = _LOAN_SELECT + " WHERE 1=1"
        params = []
        if status == 'active': sql += ' AND l.returned=0'
        elif status == 'overdue': sql += ' AND l.returned=0 AND l.due_date<?'; params.append(today)
        elif status == 'returned': sql += ' AND l.returned=1'
        if q:
            lk = f'%{q}%'
            sql += ' AND (s.name LIKE ? OR s.enrollment LIKE ? OR b.title LIKE ? OR b.patrimony LIKE ?)'
            params.extend([lk,lk,lk,lk])
        if q:
            sql += " ORDER BY CASE WHEN s.name LIKE ? THEN 0 ELSE 1 END, s.name ASC, l.borrowed_at DESC LIMIT 200"
            params.append(q + '%')
        else:
            sql += ' ORDER BY l.borrowed_at DESC LIMIT 200'
        return [_process_row(r, today) for r in c.execute(sql, params).fetchall()]
        c.commit()

def get_loan(loan_id):
    today = _today()
    with get_conn() as c:
        r = c.execute(_LOAN_SELECT + " WHERE l.id=?",(loan_id,)).fetchone()
        return _process_row(r, today) if r else None
        c.commit()

def get_active_loan_for_book(book_id):
    today = _today()
    with get_conn() as c:
        r = c.execute(_LOAN_SELECT + " WHERE l.book_id=? AND l.returned=0 LIMIT 1",(book_id,)).fetchone()
        return _process_row(r, today) if r else None
        c.commit()

def create_loan(book_id, student_id, due_date, user_id=None, borrowed_at=None):
    if borrowed_at is None:
        borrowed_at = _now()
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO loans (book_id,student_id,user_id,borrowed_at,due_date,returned) VALUES(?,?,?,?,?,0)",
                  (book_id, student_id, user_id, borrowed_at, due_date))
        lid = cur.lastrowid; conn.commit()
    return get_loan(lid)

def return_loan(loan_id):
    with get_conn() as conn:
        conn.execute("UPDATE loans SET returned=1,returned_at=? WHERE id=?",(_now(), loan_id))
        conn.commit()
    loan = get_loan(loan_id)
    if loan:
        with get_conn() as c:
            r = c.execute("""SELECT r.*, s.name as student_name, s.enrollment as student_enrollment
                            FROM reservations r
                            JOIN students s ON r.student_id=s.id
                            WHERE r.book_id=? AND r.status='active'
                            ORDER BY r.reserved_at ASC LIMIT 1""",
                          (loan['book_id'],)).fetchone()
            reservation = dict(r) if r else None
        if reservation:
            loan['has_reservation'] = True
            loan['reservation'] = reservation
        else:
            loan['has_reservation'] = False
            loan['reservation'] = None
    return loan

# ── DASHBOARD ──────────────────────────────────────────────────
def dashboard_stats():
    today = _today()
    try:
        with get_conn() as c:
            # Verificar se coluna quantity existe
            cols = [r[1] for r in c.execute("PRAGMA table_info(books)").fetchall()]
            if 'quantity' in cols:
                total_items = c.execute("SELECT COALESCE(SUM(quantity),0) FROM books WHERE active=1").fetchone()[0]
            else:
                total_items = c.execute("SELECT COUNT(*) FROM books WHERE active=1").fetchone()[0]
            return {
                'total_books': c.execute("SELECT COUNT(*) FROM books WHERE active=1").fetchone()[0],
                'total_items': total_items,
                'total_students': c.execute("SELECT COUNT(*) FROM students WHERE active=1").fetchone()[0],
                'active_loans': c.execute("SELECT COUNT(*) FROM loans WHERE returned=0").fetchone()[0],
                'overdue': c.execute("SELECT COUNT(*) FROM loans WHERE returned=0 AND due_date<?",(today,)).fetchone()[0],
                'recent_loans': list_loans('active')[:5],
                'recent_activity': list_activity(10)
            }
            c.commit()
    except Exception as e:
        import logging
        logging.error(f"Erro em dashboard_stats: {e}", exc_info=True)
        return {
            'total_books': 0, 'total_items': 0, 'total_students': 0,
            'active_loans': 0, 'overdue': 0, 'recent_loans': [], 'recent_activity': []
        }

# ── DASHBOARD CHARTS ───────────────────────────────────────────
def dashboard_charts():
    try:
        with get_conn() as c:
            # 1. Loans per day (last 30 days)
            loans_per_day = []
            for i in range(29, -1, -1):
                d = (date.today() - timedelta(days=i)).strftime('%Y-%m-%d')
                count = c.execute("SELECT COUNT(*) FROM loans WHERE date(borrowed_at)=?", (d,)).fetchone()[0]
                loans_per_day.append({'date': d, 'count': count})

            # 2. Books by category (top 8)
            cols = [r[1] for r in c.execute("PRAGMA table_info(books)").fetchall()]
            if 'category' in cols:
                rows = c.execute("""SELECT COALESCE(category,'Sem categoria') as cat, COUNT(*) as cnt 
                                    FROM books WHERE active=1 GROUP BY cat ORDER BY cnt DESC LIMIT 8""").fetchall()
                books_by_cat = [{'label': r[0], 'value': r[1]} for r in rows]
            else:
                books_by_cat = []

            # 3. Most borrowed books (top 10)
            rows = c.execute("""SELECT b.title, b.patrimony, COUNT(l.id) as cnt 
                                FROM loans l JOIN books b ON l.book_id=b.id 
                                GROUP BY l.book_id ORDER BY cnt DESC LIMIT 10""").fetchall()
            top_books = [{'title': r[0], 'patrimony': r[1], 'count': r[2]} for r in rows]

            # 4. Student class distribution (top 10)
            rows = c.execute("""SELECT COALESCE(s.class_name,'Sem turma') as cls, COUNT(l.id) as cnt 
                                FROM loans l JOIN students s ON l.student_id=s.id 
                                GROUP BY s.class_name ORDER BY cnt DESC LIMIT 10""").fetchall()
            loans_by_class = [{'label': r[0], 'value': r[1]} for r in rows]

            return {
                'loans_per_day': loans_per_day,
                'books_by_category': books_by_cat,
                'top_books': top_books,
                'loans_by_class': loans_by_class
            }
    except Exception as e:
        import logging
        logging.error(f"Erro em dashboard_charts: {e}", exc_info=True)
        return {'loans_per_day': [], 'books_by_category': [], 'top_books': [], 'loans_by_class': []}

# ── ACTIVITY ───────────────────────────────────────────────────
def list_activity(limit=50):
    try:
        with get_conn() as c:
            rows = c.execute("""SELECT a.*,u.name as user_name FROM activity_log a
                                LEFT JOIN users u ON a.user_id=u.id
                                ORDER BY a.created_at DESC LIMIT ?""",(limit,)).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d['created_at'] = _fmt_dt(d.get('created_at',''))
                d['user'] = d.get('user_name') or 'Sistema'
                result.append(d)
            return result
            c.commit()
    except Exception as e:
        import logging
        logging.error(f"Erro em list_activity: {e}", exc_info=True)
        return []

# ── REPORTS ────────────────────────────────────────────────────
def _report_loans(extra_where='', params=None):
    today = _today()
    params = params or []
    with get_conn() as c:
        sql = _LOAN_SELECT + " WHERE 1=1 " + extra_where + " ORDER BY l.due_date"
        return [_process_row(r, today) for r in c.execute(sql, params).fetchall()]
        c.commit()

def report_active_loans(class_name=''):
    w, p = '', []
    if class_name: w += ' AND s.class_name=?'; p.append(class_name)
    return _report_loans('AND l.returned=0' + w, p)

def report_overdue(class_name=''):
    today = _today()
    w, p = f' AND l.due_date<? ', [today]
    if class_name: w += ' AND s.class_name=?'; p.append(class_name)
    return _report_loans('AND l.returned=0' + w, p)

def report_student_history(student_id, date_from='', date_to=''):
    w, p = ' AND l.student_id=?', [int(student_id)]
    if date_from:
        w += ' AND l.borrowed_at>=?'; p.append(date_from + ' 00:00:00')
    if date_to:
        w += ' AND l.borrowed_at<=?'; p.append(date_to + ' 23:59:59')
    loans = _report_loans(w, p)
    with get_conn() as c:
        student = _row(c.execute("SELECT id, name, enrollment, class_name, active FROM students WHERE id=?", (int(student_id),)).fetchone()) or {}
        c.commit()
    return {'student': student, 'loans': loans, 'total': len(loans),
            'active': sum(1 for l in loans if not l['returned']),
            'returned': sum(1 for l in loans if l['returned']),
            'overdue_count': sum(1 for l in loans if l.get('is_overdue'))}

def report_movement(date_from='', date_to='', type_filter='all'):
    w, p = '', []
    if date_from: w += ' AND l.borrowed_at>=?'; p.append(date_from)
    if date_to: w += ' AND l.borrowed_at<=?'; p.append(date_to + ' 23:59:59')
    base = _report_loans(w, p)
    result = []
    for l in base:
        if type_filter in ('all','borrows'): result.append({**l,'event':'Empréstimo','event_at':l['borrowed_at']})
        if type_filter in ('all','returns') and l['returned']: result.append({**l,'event':'Devolução','event_at':l['returned_at']})
    return result

def report_inventory(category='', status=''):
    with get_conn() as c:
        borrowed_ids = set(r[0] for r in c.execute("SELECT DISTINCT book_id FROM loans WHERE returned=0").fetchall())
        q = "SELECT * FROM books WHERE active=1"
        p = []
        if category: q += ' AND category=?'; p.append(category)
        q += ' ORDER BY title'
        rows = c.execute(q, p).fetchall()
        c.commit()
    result = []
    for r in rows:
        d = _book_dict(r)
        if d:
            d['available'] = d['id'] not in borrowed_ids
            result.append(d)
    status = status.split(':')[0] if ':' in str(status) else status
    if status == 'available': return [b for b in result if b['available']]
    if status == 'borrowed': return [b for b in result if not b['available']]
    return result

def report_most_borrowed(date_from='', date_to='', category=''):
    with get_conn() as c:
        q = "SELECT b.id,b.title,b.author,b.patrimony,b.category,COUNT(l.id) as total_loans FROM books b JOIN loans l ON b.id=l.book_id WHERE 1=1"
        p = []
        if date_from: q += ' AND l.borrowed_at>=?'; p.append(date_from)
        if date_to: q += ' AND l.borrowed_at<=?'; p.append(date_to + ' 23:59:59')
        if category: q += ' AND b.category=?'; p.append(category)
        q += ' GROUP BY b.id ORDER BY total_loans DESC LIMIT 20'
        result = [dict(r) for r in c.execute(q, p).fetchall()]
        c.commit()
        return result

def get_classes():
    with get_conn() as c:
        result = [r[0] for r in c.execute("SELECT DISTINCT class_name FROM students WHERE class_name!='' AND active=1 ORDER BY class_name").fetchall()]
        c.commit()
        return result

def report_student_ranking(date_from='', date_to='', class_name='', student_id='', min_loans=0):
    """Relatório de alunos com mais empréstimos em um período"""
    with get_conn() as c:
        where_cond = ["l.id IS NOT NULL"]
        params = []
        if date_from:
            where_cond.append("l.borrowed_at >= ?"); params.append(date_from)
        if date_to:
            where_cond.append("l.borrowed_at <= ?"); params.append(date_to + ' 23:59:59')
        if class_name:
            where_cond.append("s.class_name = ?"); params.append(class_name)
        if student_id:
            where_cond.append("s.id = ?"); params.append(student_id)

        q = f"""SELECT s.id, s.name, s.enrollment, s.class_name,
                   COUNT(l.id) as total_loans,
                   MIN(l.borrowed_at) as first_loan,
                   MAX(l.borrowed_at) as last_loan
            FROM students s
            JOIN loans l ON s.id = l.student_id
            WHERE {' AND '.join(where_cond)}
            GROUP BY s.id
            ORDER BY total_loans DESC
            LIMIT 200"""

        rows = c.execute(q, params).fetchall()
        result = [dict(r) for r in rows]
        if min_loans:
            result = [r for r in result if r['total_loans'] >= int(min_loans)]
        return result

def report_class_ranking(date_from='', date_to=''):
    """Relatório de turmas com mais empréstimos em um período"""
    with get_conn() as c:
        where_cond = ["s.class_name IS NOT NULL", "s.class_name != ''", "l.id IS NOT NULL"]
        params = []
        if date_from:
            where_cond.append("l.borrowed_at >= ?"); params.append(date_from)
        if date_to:
            where_cond.append("l.borrowed_at <= ?"); params.append(date_to + ' 23:59:59')

        q = f"""SELECT s.class_name,
                   COUNT(DISTINCT s.id) as total_students,
                   COUNT(l.id) as total_loans,
                   ROUND(CAST(COUNT(l.id) AS FLOAT) / MAX(1, COUNT(DISTINCT s.id)), 1) as avg_per_student
            FROM students s
            JOIN loans l ON s.id = l.student_id
            WHERE {' AND '.join(where_cond)}
            GROUP BY s.class_name
            ORDER BY total_loans DESC"""

        rows = c.execute(q, params).fetchall()
        return [dict(r) for r in rows]

def get_categories():
    with get_conn() as c:
        result = [r[0] for r in c.execute("SELECT DISTINCT name FROM categories WHERE active=1 ORDER BY name").fetchall()]
        c.commit()
        return result

def list_categories():
    with get_conn() as c:
        result = [dict(r) for r in c.execute("SELECT * FROM categories WHERE active=1 ORDER BY name").fetchall()]
        c.commit()
        return result

def create_category(name):
    with get_conn() as conn:
        conn.execute("INSERT INTO categories (name, active) VALUES (?, 1)", (name.strip(),))
        conn.commit()
        return {'name': name.strip(), 'active': 1}

def delete_category(cat_id):
    with get_conn() as conn:
        conn.execute("UPDATE categories SET active=0 WHERE id=?", (cat_id,))
        conn.commit()

def global_search(q):
    lk = f'%{q}%'
    with get_conn() as c:
        books = [dict(r) for r in c.execute("SELECT id,title,author,patrimony FROM books WHERE active=1 AND (title LIKE ? OR author LIKE ? OR patrimony LIKE ?) LIMIT 5",(lk,lk,lk)).fetchall()]
        students = [dict(r) for r in c.execute("SELECT id,name,enrollment,class_name FROM students WHERE active=1 AND (name LIKE ? OR enrollment LIKE ?) LIMIT 5",(lk,lk)).fetchall()]
        c.commit()
    return {'books': books, 'students': students}

# ── LICENSE ────────────────────────────────────────────────────
def get_license():
    with get_conn() as c:
        return _row(c.execute("SELECT * FROM license_info LIMIT 1").fetchone())

def is_license_valid():
    """Check if license is valid and not expired."""
    lic = get_license()
    if not lic or not lic.get('is_valid'):
        return False
    valid_until = lic.get('valid_until')
    if not valid_until:
        return False
    try:
        from datetime import date
        if '-' in valid_until:
            # ISO format: YYYY-MM-DD
            parts = valid_until.split('-')
            exp_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        elif '/' in valid_until:
            # Brazilian format: DD/MM/YYYY
            parts = valid_until.split('/')
            exp_date = date(int(parts[2]), int(parts[1]), int(parts[0]))
        else:
            return False
        return date.today() <= exp_date
    except:
        return False

def save_license(machine_id, key, institution, valid_until_date):
    with get_conn() as conn:
        if conn.execute("SELECT id FROM license_info LIMIT 1").fetchone():
            conn.execute("UPDATE license_info SET machine_id=?,license_key=?,institution_name=?,valid_until=?,activated_at=?,is_valid=1 WHERE id=1",
                      (machine_id, key, institution, valid_until_date.isoformat(), _now()))
        else:
            conn.execute("INSERT INTO license_info (machine_id,license_key,institution_name,valid_until,activated_at,is_valid) VALUES(?,?,?,?,?,1)",
                      (machine_id, key, institution, valid_until_date.isoformat(), _now()))
        conn.commit()

def invalidate_license():
    with get_conn() as conn:
        conn.execute("UPDATE license_info SET is_valid=0")
        conn.commit()

# ── OPERATOR PERMISSIONS ───────────────────────────────────────
PERM_FIELDS = ['can_create_books','can_edit_books','can_delete_books','can_create_students','can_edit_students','can_delete_students','can_create_loans','can_return_books','can_renew_loans','can_manage_reservations','can_view_reports','can_print_barcodes','can_manage_categories','can_backup','can_view_activity']

def get_operator_permissions():
    try:
        with get_conn() as c:
            row = c.execute("SELECT * FROM operator_permissions WHERE id=1").fetchone()
            if row:
                c.commit()
                return dict(row)
            # Criar registro padrão
            defaults = ["1" if f not in ('can_delete_books', 'can_delete_students', 'can_manage_categories', 'can_backup') else "0" for f in PERM_FIELDS]
            c.execute("INSERT INTO operator_permissions (id," + ",".join(PERM_FIELDS) + ",updated_at) VALUES(1," + ",".join(defaults) + ",?)", (_now(),))
            c.commit()
            row = c.execute("SELECT * FROM operator_permissions WHERE id=1").fetchone()
            return dict(row) if row else {}
    except Exception as e:
        import logging
        logging.error(f"Erro em get_operator_permissions: {e}", exc_info=True)
        return {}

def save_operator_permissions(perms):
    fields = ",".join([f"{f}=?" for f in PERM_FIELDS])
    data = [1 if perms.get(f, False) else 0 for f in PERM_FIELDS] + [_now()]
    with get_conn() as conn:
        conn.execute(f"INSERT OR REPLACE INTO operator_permissions (id,{','.join(PERM_FIELDS)},updated_at) VALUES(1,{','.join(['?']*len(PERM_FIELDS))},?)", data)
        conn.commit()
