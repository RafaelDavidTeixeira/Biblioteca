"""
Business logic layer.
Coordinates data access (database.py) with business rules and validations.
"""
from datetime import date, datetime, timedelta
from . import database as db


def renew_loan(loan_id, extra_days=None):
    from datetime import date, timedelta
    with db.get_conn() as c:
        inst = c.execute("SELECT loan_days_default FROM institution LIMIT 1").fetchone()
        loan_days = (inst[0] if inst and inst[0] else 14)
        if extra_days is not None:
            loan_days = extra_days
        r = c.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
        if not r:
            return None, 'Emprstimo no encontrado'
        r = dict(r)
        if r['returned']:
            return None, 'Emprstimo j devolvido'
        has_reservation = c.execute("""SELECT id FROM reservations
                                       WHERE book_id=? AND status='active' AND student_id!=?""",
                                    (r['book_id'], r['student_id'])).fetchone()
        if has_reservation:
            return None, 'Este livro possui reserva de outro aluno'
        try:
            current_due = date.fromisoformat(r['due_date'])
        except:
            return None, 'Data de devoluo invlida'
        new_due = current_due + timedelta(days=loan_days)
        c.execute("UPDATE loans SET due_date=?, renewed=renewed+1, renewed_at=? WHERE id=?",
                  (new_due.isoformat(), db._now(), loan_id))
        c.commit()
        db_loan = db.get_loan(loan_id)
        return db_loan, None


def create_reservation(book_id, student_id, user_id=None):
    with db.get_conn() as c:
        existing = c.execute("""SELECT id FROM reservations
                                WHERE book_id=? AND student_id=? AND status='active'""",
                             (book_id, student_id)).fetchone()
        if existing:
            return None, 'Reserva j existe para este aluno'
        active_loan = c.execute("SELECT id FROM loans WHERE book_id=? AND returned=0", (book_id,)).fetchone()
        if not active_loan:
            return None, 'Livro disponvel - faa o emprstimo direto'
        self_loan = c.execute("SELECT id FROM loans WHERE book_id=? AND student_id=? AND returned=0", (book_id, student_id)).fetchone()
        if self_loan:
            return None, 'Aluno j possui este livro emprestado'
        cur = c.execute("""INSERT INTO reservations (book_id, student_id, user_id, reserved_at, status)
                          VALUES(?,?,?,?, 'active')""",
                        (book_id, student_id, user_id, db._now()))
        c.commit()
        return cur.lastrowid, None


def cancel_reservation(reservation_id):
    with db.get_conn() as c:
        c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (reservation_id,))
        c.commit()
        return True


def cancel_student_reservations(student_id):
    with db.get_conn() as c:
        c.execute("UPDATE reservations SET status='cancelled' WHERE student_id=? AND status='active'", (student_id,))
        c.commit()


def get_reservation_by_student_and_book(student_id, book_id):
    with db.get_conn() as c:
        r = c.execute("""SELECT r.*, s.name as student_name, b.title as book_title, b.patrimony as book_patrimony
                        FROM reservations r
                        JOIN students s ON r.student_id=s.id
                        JOIN books b ON r.book_id=b.id
                        WHERE r.student_id=? AND r.book_id=? AND r.status='active'""",
                      (student_id, book_id)).fetchone()
        return dict(r) if r else None


def get_active_reservations(book_id=None):
    with db.get_conn() as c:
        sql = """SELECT r.*, s.name as student_name, s.enrollment as student_enrollment,
                        b.title as book_title, b.patrimony as book_patrimony, u.name as operator_name
                 FROM reservations r
                 JOIN students s ON r.student_id=s.id
                 JOIN books b ON r.book_id=b.id
                 LEFT JOIN users u ON r.user_id=u.id
                 WHERE r.status='active'"""
        params = []
        if book_id:
            sql += ' AND r.book_id=?'
            params.append(book_id)
        sql += ' ORDER BY r.reserved_at ASC'
        rows = c.execute(sql, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['reserved_at'] = db._fmt_dt(d.get('reserved_at', ''))
            result.append(d)
        return result


def get_next_reservation_for_book(book_id):
    with db.get_conn() as c:
        r = c.execute("""SELECT r.*, s.name as student_name, s.enrollment as student_enrollment
                        FROM reservations r
                        JOIN students s ON r.student_id=s.id
                        WHERE r.book_id=? AND r.status='active'
                        ORDER BY r.reserved_at ASC LIMIT 1""",
                      (book_id,)).fetchone()
        return dict(r) if r else None


def check_reservation_on_loan(book_id, student_id):
    with db.get_conn() as c:
        r = c.execute("""SELECT r.*, s.name as student_name, s.enrollment as student_enrollment
                        FROM reservations r
                        JOIN students s ON r.student_id=s.id
                        WHERE r.book_id=? AND r.status='active'
                        ORDER BY r.reserved_at ASC LIMIT 1""",
                      (book_id,)).fetchone()
        if r:
            if r['student_id'] == student_id:
                fulfill_reservation(book_id, student_id)
                return None
            else:
                return dict(r)
        return None


def fulfill_reservation(book_id, student_id):
    with db.get_conn() as c:
        c.execute("""UPDATE reservations SET status='fulfilled'
                     WHERE book_id=? AND student_id=? AND status='active'""",
                  (book_id, student_id))
        c.commit()


def get_reservation_stats():
    with db.get_conn() as c:
        total = c.execute("SELECT COUNT(*) FROM reservations WHERE status='active'").fetchone()[0]
        fulfilled = c.execute("SELECT COUNT(*) FROM reservations WHERE status='fulfilled'").fetchone()[0]
        cancelled = c.execute("SELECT COUNT(*) FROM reservations WHERE status='cancelled'").fetchone()[0]
        return {'total_active': total, 'total_fulfilled': fulfilled, 'total_cancelled': cancelled}


def get_reservations_report(status='active'):
    with db.get_conn() as c:
        sql = """SELECT r.*, s.name as student_name, s.enrollment as student_enrollment, s.class_name as student_class,
                        b.title as book_title, b.patrimony as book_patrimony, b.category as book_category,
                        u.name as operator_name
                 FROM reservations r
                 JOIN students s ON r.student_id=s.id
                 JOIN books b ON r.book_id=b.id
                 LEFT JOIN users u ON r.user_id=u.id
                 WHERE 1=1"""
        params = []
        if status != 'all':
            sql += " AND r.status=?"
            params.append(status)
        sql += " ORDER BY r.reserved_at ASC"
        rows = c.execute(sql, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['reserved_at'] = db._fmt_dt(d.get('reserved_at', ''))
            status_labels = {'active': 'Ativa', 'fulfilled': 'Atendida', 'cancelled': 'Cancelada'}
            d['status_label'] = status_labels.get(d.get('status', ''), d.get('status', ''))
            result.append(d)
        return result
