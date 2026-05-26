from flask import Blueprint, request, jsonify, session, render_template
from datetime import date, datetime, timedelta
from .. import database as db
from .. import services
from .auth import auth_required
from .settings import has_operator_permission

bp = Blueprint('loans', __name__)


@bp.route('/emprestimos')
@auth_required
def loans_page():
    inst = db.get_institution()
    return render_template('app.html', page='loans', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/reservas')
@auth_required
def reservations_page():
    inst = db.get_institution()
    return render_template('app.html', page='reservations', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/loans', methods=['GET'])
@auth_required
def get_loans():
    return jsonify(db.list_loans(request.args.get('status', 'active'), request.args.get('q', '')))


@bp.route('/api/loans/<int:lid>', methods=['GET'])
@auth_required
def get_loan(lid):
    l = db.get_loan(lid)
    if not l: return jsonify({'error': 'Não encontrado'}), 404
    return jsonify(l)


@bp.route('/api/loans', methods=['POST'])
@auth_required
def create_loan():
    if not has_operator_permission('can_create_loans'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    book_id = data.get('book_id')
    student_id = data.get('student_id')
    due_date_str = data.get('due_date')
    due_days = data.get('due_days')
    borrowed_at = data.get('borrowed_at')

    if not book_id or not student_id:
        return jsonify({'error': 'Livro e aluno são obrigatórios'}), 400

    book = db.get_book(book_id)
    if not book: return jsonify({'error': 'Livro não encontrado'}), 404
    if not book['available']: return jsonify({'error': f'Livro "{book["title"]}" já está emprestado'}), 400

    student = db.get_student(student_id)
    if not student: return jsonify({'error': 'Aluno não encontrado'}), 404

    reservation = services.check_reservation_on_loan(book_id, student_id)
    if reservation:
        return jsonify({
            'error': f'Este livro está reservado por {reservation["student_name"]} ({reservation["student_enrollment"]})',
            'has_reservation': True,
            'reservation': reservation
        }), 409

    if due_date_str:
        try: due_date = date.fromisoformat(due_date_str)
        except: return jsonify({'error': 'Data inválida'}), 400
    elif due_days:
        due_date = date.today() + timedelta(days=int(due_days))
    else:
        inst = db.get_institution()
        due_date = date.today() + timedelta(days=(inst or {}).get('loan_days_default', 14))

    if borrowed_at:
        try:
            borrowed_at_dt = datetime.fromisoformat(borrowed_at)
            borrowed_at = borrowed_at_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return jsonify({'error': 'Data/hora do empréstimo inválida'}), 400

    loan = db.create_loan(book_id, student_id, due_date.isoformat(), session.get('user_id'), borrowed_at)
    db.log_activity('borrow', f'{student["name"]} pegou "{book["title"]}" ({book["patrimony"]}) — dev: {due_date.strftime("%d/%m/%Y")}', session.get('user_id'))
    return jsonify({'ok': True, 'loan': loan})


@bp.route('/api/loans/batch', methods=['POST'])
@auth_required
def create_batch_loans():
    if not has_operator_permission('can_create_loans'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    book_ids = data.get('book_ids', [])
    student_id = data.get('student_id')
    due_date_str = data.get('due_date')
    due_days = data.get('due_days')
    borrowed_at = data.get('borrowed_at')

    if not book_ids or not student_id:
        return jsonify({'error': 'Aluno e pelo menos um livro são obrigatórios'}), 400

    student = db.get_student(student_id)
    if not student: return jsonify({'error': 'Aluno não encontrado'}), 404

    if due_date_str:
        try: due_date = date.fromisoformat(due_date_str)
        except: return jsonify({'error': 'Data inválida'}), 400
    elif due_days:
        due_date = date.today() + timedelta(days=int(due_days))
    else:
        inst = db.get_institution()
        due_date = date.today() + timedelta(days=(inst or {}).get('loan_days_default', 14))

    if borrowed_at:
        try:
            borrowed_at_dt = datetime.fromisoformat(borrowed_at)
            borrowed_at = borrowed_at_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return jsonify({'error': 'Data/hora do empréstimo inválida'}), 400

    success = []
    errors = []
    for book_id in book_ids:
        book = db.get_book(book_id)
        if not book:
            errors.append(f'Livro ID {book_id} não encontrado')
            continue
        if not book['available']:
            errors.append(f'Livro "{book["title"]}" ({book["patrimony"]}) já está emprestado')
            continue
        reservation = services.check_reservation_on_loan(book_id, student_id)
        if reservation:
            errors.append(f'Livro "{book["title"]}" ({book["patrimony"]}) reservado por {reservation["student_name"]}')
            continue
        try:
            loan = db.create_loan(book_id, student_id, due_date.isoformat(), session.get('user_id'), borrowed_at)
            db.log_activity('borrow', f'{student["name"]} pegou "{book["title"]}" ({book["patrimony"]}) — dev: {due_date.strftime("%d/%m/%Y")}', session.get('user_id'))
            success.append({'book_title': book['title'], 'patrimony': book['patrimony'], 'loan_id': loan['id']})
        except Exception as e:
            errors.append(f'Erro ao registrar "{book["title"]}": {str(e)}')

    result = {'success': success, 'errors': errors, 'total': len(success)}
    if not success and errors:
        return jsonify({'error': '; '.join(errors)}), 400
    return jsonify({'ok': True, 'result': result})


@bp.route('/api/loans/<int:lid>/return', methods=['POST'])
@auth_required
def return_loan(lid):
    if not has_operator_permission('can_return_books'):
        return jsonify({'error': 'Permissao negada'}), 403
    loan = db.get_loan(lid)
    if not loan: return jsonify({'error': 'Não encontrado'}), 404
    if loan['returned']: return jsonify({'error': 'Livro já foi devolvido'}), 400
    loan = db.return_loan(lid)
    msg = f'{loan["student_name"]} devolveu "{loan["book_title"]}" ({loan["book_patrimony"]})'
    if loan.get('has_reservation') and loan.get('reservation'):
        msg += f' — LIVRO RESERVADO por {loan["reservation"]["student_name"]} ({loan["reservation"]["student_enrollment"]})'
    db.log_activity('return', msg, session.get('user_id'))
    return jsonify({
        'ok': True,
        'loan': loan,
        'has_reservation': loan.get('has_reservation', False),
        'reservation': loan.get('reservation')
    })


@bp.route('/api/loans/return-by-patrimony', methods=['POST'])
@auth_required
def return_by_patrimony():
    if not has_operator_permission('can_return_books'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    patrimony = (data.get('patrimony') or '').strip().upper()
    book = db.get_book_by_patrimony(patrimony)
    if not book: return jsonify({'error': f'Patrimônio {patrimony} não encontrado'}), 404
    loan = db.get_active_loan_for_book(book['id'])
    if not loan: return jsonify({'error': f'Nenhum empréstimo ativo para {patrimony}'}), 404
    loan = db.return_loan(loan['id'])
    msg = f'{loan["student_name"]} devolveu "{loan["book_title"]}" ({patrimony})'
    if loan.get('has_reservation') and loan.get('reservation'):
        msg += f' — LIVRO RESERVADO por {loan["reservation"]["student_name"]} ({loan["reservation"]["student_enrollment"]})'
    db.log_activity('return', msg, session.get('user_id'))
    return jsonify({
        'ok': True,
        'loan': loan,
        'has_reservation': loan.get('has_reservation', False),
        'reservation': loan.get('reservation')
    })


@bp.route('/api/loans/lookup-patrimony/<patrimony>')
@auth_required
def lookup_patrimony(patrimony):
    book = db.get_book_by_patrimony(patrimony)
    if not book: return jsonify({'error': 'Patrimônio não encontrado'}), 404
    loan = db.get_active_loan_for_book(book['id'])
    if not loan: return jsonify({'error': 'Nenhum empréstimo ativo para este livro'}), 404
    return jsonify(loan)


@bp.route('/api/loans/<int:lid>/renew', methods=['POST'])
@auth_required
def renew_loan(lid):
    if not has_operator_permission('can_renew_loans'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json(silent=True) or {}
    extra_days = data.get('extra_days')
    loan, err = services.renew_loan(lid, extra_days)
    if err:
        return jsonify({'error': err}), 400
    db.log_activity('renew', f'"{loan["book_title"]}" ({loan["book_patrimony"]}) renovado — nova devolução: {loan["due_date"]} (renovações: {loan["renewed"]})', session.get('user_id'))
    return jsonify({'ok': True, 'loan': loan})


@bp.route('/api/loans/batch-renew', methods=['POST'])
@auth_required
def batch_renew_loans():
    data = request.get_json(silent=True) or {}
    loan_ids = data.get('loan_ids', [])
    extra_days = data.get('extra_days')
    if not loan_ids:
        return jsonify({'error': 'Nenhum empréstimo selecionado'}), 400
    success = []
    errors = []
    for lid in loan_ids:
        loan, err = services.renew_loan(lid, extra_days)
        if err:
            errors.append({'loan_id': lid, 'error': err})
        else:
            db.log_activity('renew', f'"{loan["book_title"]}" ({loan["book_patrimony"]}) renovado', session.get('user_id'))
            success.append({'loan_id': lid, 'book_title': loan['book_title'], 'new_due_date': loan['due_date']})
    return jsonify({'ok': True, 'success': success, 'errors': errors})


@bp.route('/api/reservations', methods=['GET'])
@auth_required
def get_reservations():
    book_id = request.args.get('book_id', type=int)
    return jsonify(services.get_active_reservations(book_id))


@bp.route('/api/reservations', methods=['POST'])
@auth_required
def create_reservation():
    if not has_operator_permission('can_manage_reservations'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    book_id = data.get('book_id')
    student_id = data.get('student_id')
    if not book_id or not student_id:
        return jsonify({'error': 'Livro e aluno são obrigatórios'}), 400
    res, err = services.create_reservation(book_id, student_id, session.get('user_id'))
    if err:
        return jsonify({'error': err}), 400
    book = db.get_book(book_id)
    student = db.get_student(student_id)
    db.log_activity('reserve', f'Reserva: {student["name"]} -> "{book["title"]}" ({book["patrimony"]})', session.get('user_id'))
    return jsonify({'ok': True, 'reservation_id': res})


@bp.route('/api/reservations/<int:rid>', methods=['DELETE'])
@auth_required
def cancel_reservation(rid):
    if not has_operator_permission('can_manage_reservations'):
        return jsonify({'error': 'Permissao negada'}), 403
    services.cancel_reservation(rid)
    return jsonify({'ok': True})


@bp.route('/api/reservations/<int:rid>/fulfill', methods=['POST'])
@auth_required
def fulfill_reservation(rid):
    if not has_operator_permission('can_create_loans'):
        return jsonify({'error': 'Permissao negada'}), 403
    try:
        with db.get_conn() as c:
            res = c.execute("SELECT * FROM reservations WHERE id=?", (rid,)).fetchone()
            if not res: return jsonify({'error': 'Reserva não encontrada'}), 404
            if res['status'] != 'active': return jsonify({'error': 'Reserva já não está ativa'}), 400
            book = db.get_book(res['book_id'])
            if not book: return jsonify({'error': 'Livro não encontrado'}), 404
            if not book['available']: return jsonify({'error': 'Livro já está emprestado'}), 400
            # Verificar fila de reservas
            first = c.execute("""SELECT r.id, s.name as student_name FROM reservations r
                                 JOIN students s ON r.student_id=s.id
                                 WHERE r.book_id=? AND r.status='active'
                                 ORDER BY r.reserved_at ASC LIMIT 1""",
                              (res['book_id'],)).fetchone()
            if first and first['id'] != rid:
                return jsonify({'error': f'Existe uma reserva mais antiga de {first["student_name"]}. Atenda essa primeiro.'}), 409
            inst = db.get_institution()
            due_days = inst.get('loan_days_default', 14) if inst else 14
            due = (date.today() + timedelta(days=int(due_days))).isoformat()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO loans (book_id, student_id, user_id, borrowed_at, due_date) VALUES (?,?,?,?,?)",
                      (res['book_id'], res['student_id'], session.get('user_id'), now, due))
            c.execute("UPDATE reservations SET status='fulfilled' WHERE id=?", (rid,))
            c.commit()
        db.log_activity('loan', f'Empréstimo via reserva: {book["title"]} ({book["patrimony"]})', session.get('user_id'))
        return jsonify({'ok': True})
    except Exception as e:
        import logging
        logging.error(f"Erro ao atender reserva {rid}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/api/reservations/check/<int:student_id>/<int:book_id>')
@auth_required
def check_reservation(student_id, book_id):
    res = services.get_reservation_by_student_and_book(student_id, book_id)
    return jsonify({'reservation': res})
