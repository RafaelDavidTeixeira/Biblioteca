from flask import Blueprint, request, jsonify, session, render_template
from datetime import date, timedelta
from .. import database as db
from .auth import auth_required
from .settings import has_operator_permission

bp = Blueprint('loans', __name__)


@bp.route('/emprestimos')
@auth_required
def loans_page():
    inst = db.get_institution()
    return render_template('app.html', page='loans', institution=inst,
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

    if not book_id or not student_id:
        return jsonify({'error': 'Livro e aluno são obrigatórios'}), 400

    book = db.get_book(book_id)
    if not book: return jsonify({'error': 'Livro não encontrado'}), 404
    if not book['available']: return jsonify({'error': f'Livro "{book["title"]}" já está emprestado'}), 400

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

    loan = db.create_loan(book_id, student_id, due_date.isoformat(), session.get('user_id'))
    db.log_activity('borrow', f'{student["name"]} pegou "{book["title"]}" ({book["patrimony"]}) — dev: {due_date.strftime("%d/%m/%Y")}', session.get('user_id'))
    return jsonify({'ok': True, 'loan': loan})


@bp.route('/api/loans/<int:lid>/return', methods=['POST'])
@auth_required
def return_loan(lid):
    if not has_operator_permission('can_return_books'):
        return jsonify({'error': 'Permissao negada'}), 403
    loan = db.get_loan(lid)
    if not loan: return jsonify({'error': 'Não encontrado'}), 404
    if loan['returned']: return jsonify({'error': 'Livro já foi devolvido'}), 400
    loan = db.return_loan(lid)
    db.log_activity('return', f'{loan["student_name"]} devolveu "{loan["book_title"]}" ({loan["book_patrimony"]})', session.get('user_id'))
    return jsonify({'ok': True, 'loan': loan})


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
    db.log_activity('return', f'{loan["student_name"]} devolveu "{loan["book_title"]}" ({patrimony})', session.get('user_id'))
    return jsonify({'ok': True, 'loan': loan})


@bp.route('/api/loans/lookup-patrimony/<patrimony>')
@auth_required
def lookup_patrimony(patrimony):
    book = db.get_book_by_patrimony(patrimony)
    if not book: return jsonify({'error': 'Patrimônio não encontrado'}), 404
    loan = db.get_active_loan_for_book(book['id'])
    if not loan: return jsonify({'error': 'Nenhum empréstimo ativo para este livro'}), 404
    return jsonify(loan)
