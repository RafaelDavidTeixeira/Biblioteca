from flask import Blueprint, render_template, request, jsonify, session, current_app, send_file
from .. import database as db
from .auth import auth_required, admin_required
from .settings import has_operator_permission

bp = Blueprint('books', __name__)


@bp.route('/dashboard')
@auth_required
def dashboard():
    inst = db.get_institution()
    return render_template('app.html', page='dashboard', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/livros')
@auth_required
def books_page():
    inst = db.get_institution()
    return render_template('app.html', page='books', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/dashboard/stats')
@auth_required
def dashboard_stats():
    return jsonify(db.dashboard_stats())


@bp.route('/api/books', methods=['GET'])
@auth_required
def get_books():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    return jsonify(db.list_books(q, page, per_page))


@bp.route('/api/books/<int:book_id>', methods=['GET'])
@auth_required
def get_book(book_id):
    b = db.get_book(book_id)
    if not b: return jsonify({'error': 'Não encontrado'}), 404
    return jsonify(b)


@bp.route('/api/books/by-patrimony/<patrimony>')
@auth_required
def get_book_by_patrimony(patrimony):
    b = db.get_book_by_patrimony(patrimony)
    if not b: return jsonify({'error': 'Livro não encontrado'}), 404
    return jsonify(b)


@bp.route('/api/books', methods=['POST'])
@auth_required
def create_book():
    if not has_operator_permission('can_create_books'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    patrimony = (data.get('patrimony') or '').strip().upper()
    title = (data.get('title') or '').strip()
    if not patrimony or not title:
        return jsonify({'error': 'Patrimônio e título são obrigatórios'}), 400
    if db.get_book_by_patrimony(patrimony):
        return jsonify({'error': f'Patrimônio {patrimony} já cadastrado'}), 400
    book = db.create_book(data)
    db.log_activity('register_book', f'Livro cadastrado: "{book["title"]}" ({book["patrimony"]})', session.get('user_id'))
    return jsonify({'ok': True, 'book': book})


@bp.route('/api/books/<int:book_id>', methods=['PUT'])
@auth_required
def update_book(book_id):
    if not has_operator_permission('can_edit_books'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    if not (data.get('title') or '').strip():
        return jsonify({'error': 'Título é obrigatório'}), 400
    old_book = db.get_book(book_id)
    # Check if patrimony is being changed and if it already exists
    new_patrimony = (data.get('patrimony') or '').strip().upper()
    if new_patrimony and new_patrimony != old_book.get('patrimony', ''):
        existing = db.get_book_by_patrimony(new_patrimony)
        if existing and existing['id'] != book_id:
            return jsonify({'error': f'Patrimônio {new_patrimony} já cadastrado para outro livro'}), 400
    book = db.update_book(book_id, data)
    changes = []
    if old_book:
        for k in ['patrimony', 'title', 'author', 'isbn', 'category', 'publisher', 'year', 'notes']:
            old_val = str(old_book.get(k, '') or '')
            new_val = str(data.get(k, '') or '')
            if old_val != new_val:
                changes.append(f'{k}: "{old_val}" → "{new_val}"')
    if changes:
        db.log_activity('update_book', f'Livro editado: "{book["title"]}" ({book["patrimony"]}) — {", ".join(changes)}', session.get('user_id'))
    return jsonify({'ok': True, 'book': book})


@bp.route('/api/books/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    b = db.get_book(book_id)
    if not b: return jsonify({'error': 'Não encontrado'}), 404
    if not b['available']: return jsonify({'error': 'Livro com empréstimo ativo'}), 400
    db.deactivate_book(book_id)
    db.log_activity('delete_book', f'Livro removido: "{b["title"]}" ({b["patrimony"]})', session.get('user_id'))
    return jsonify({'ok': True})


@bp.route('/api/books/import-csv', methods=['POST'])
@auth_required
def import_books_csv():
    import csv, io
    file = request.files.get('file')
    if not file: return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    content = file.read().decode('utf-8-sig', errors='replace')
    reader = csv.DictReader(io.StringIO(content))
    imported, skipped, errors = 0, 0, []
    for i, row in enumerate(reader, 1):
        try:
            pat = (row.get('patrimonio') or row.get('patrimônio') or row.get('PAT') or '').strip().upper()
            title = (row.get('titulo') or row.get('título') or row.get('title') or '').strip()
            if not pat or not title: errors.append(f'Linha {i}: patrimônio ou título vazio'); skipped += 1; continue
            if db.get_book_by_patrimony(pat): errors.append(f'Linha {i}: patrimônio {pat} já existe'); skipped += 1; continue
            year_val = (row.get('year') or row.get('ano') or '').strip()
            year = int(year_val) if year_val.isdigit() else None
            db.create_book({'patrimony': pat, 'title': title,
                            'author': (row.get('autor') or row.get('author') or '').strip(),
                            'isbn': (row.get('isbn') or '').strip(),
                            'category': (row.get('categoria') or row.get('category') or '').strip(),
                            'publisher': (row.get('editora') or row.get('publisher') or '').strip(),
                            'year': year})
            imported += 1
        except Exception as e:
            errors.append(f'Linha {i}: {e}')
    db.log_activity('import_books', f'CSV: {imported} livros importados, {skipped} ignorados', session.get('user_id'))
    return jsonify({'ok': True, 'imported': imported, 'skipped': skipped, 'errors': errors[:20]})


@bp.route('/api/books/<int:book_id>/barcode')
@auth_required
def get_barcode(book_id):
    import io
    import barcode
    from barcode.writer import ImageWriter
    b = db.get_book(book_id)
    if not b:
        return jsonify({'error': 'Não encontrado'}), 404
    try:
        code128 = barcode.get('code128', b['patrimony'], writer=ImageWriter())
        img_io = io.BytesIO()
        code128.write(img_io, options={
            'module_width': 0.4,
            'module_height': 15.0,
            'quiet_zone': 6.0,
            'font_size': 10,
            'text_distance': 5.0
        })
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar código de barras: {e}'}), 500
