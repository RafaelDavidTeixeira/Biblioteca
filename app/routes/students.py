from flask import Blueprint, request, jsonify, session, render_template
from .. import database as db
from .. import services
from .auth import auth_required, admin_required
from .settings import has_operator_permission

bp = Blueprint('students', __name__)


@bp.route('/alunos')
@auth_required
def students_page():
    inst = db.get_institution()
    return render_template('app.html', page='students', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/students', methods=['GET'])
@auth_required
def get_students():
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    return jsonify(db.list_students(request.args.get('q', ''), request.args.get('active', 'active'), sort_by, sort_order))


@bp.route('/api/students/<int:sid>', methods=['GET'])
@auth_required
def get_student(sid):
    s = db.get_student(sid)
    if not s: return jsonify({'error': 'Não encontrado'}), 404
    return jsonify(s)


@bp.route('/api/students/by-enrollment/<enrollment>')
@auth_required
def get_by_enrollment(enrollment):
    s = db.get_student_by_enrollment(enrollment)
    if not s: return jsonify({'error': 'Aluno não encontrado'}), 404
    return jsonify(s)


@bp.route('/api/students', methods=['POST'])
@auth_required
def create_student():
    if not has_operator_permission('can_create_students'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    name = (data.get('name') or '').strip()
    enrollment = (data.get('enrollment') or '').strip()
    if not name or not enrollment:
        return jsonify({'error': 'Nome e matrícula são obrigatórios'}), 400
    if db.get_student_by_enrollment(enrollment):
        return jsonify({'error': f'Matrícula {enrollment} já cadastrada'}), 400
    s = db.create_student(data)
    db.log_activity('register_student', f'Aluno cadastrado: {s["name"]} ({s["enrollment"]})', session.get('user_id'))
    return jsonify({'ok': True, 'student': s})


@bp.route('/api/students/<int:sid>', methods=['PUT'])
@auth_required
def update_student(sid):
    if not has_operator_permission('can_edit_students'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    print(f"DEBUG PUT /api/students/{sid}: received data = {data}")
    if not (data.get('name') or '').strip():
        return jsonify({'error': 'Nome é obrigatório'}), 400
    old_student = db.get_student(sid)
    print(f"DEBUG: old_student enrollment = {old_student.get('enrollment')}")
    # Check if enrollment is being changed and if it already exists
    new_enrollment = (data.get('enrollment') or '').strip()
    print(f"DEBUG: new_enrollment = {new_enrollment}")
    if new_enrollment and new_enrollment != old_student.get('enrollment', ''):
        existing = db.get_student_by_enrollment(new_enrollment)
        if existing and existing['id'] != sid:
            return jsonify({'error': f'Matrícula {new_enrollment} já cadastrada para outro aluno'}), 400
    s = db.update_student(sid, data)
    print(f"DEBUG: after update, student enrollment = {s.get('enrollment')}")
    changes = []
    if old_student:
        for k in ['name', 'enrollment', 'class_name', 'phone', 'email', 'notes']:
            old_val = str(old_student.get(k, '') or '')
            new_val = str(data.get(k, '') or '')
            if old_val != new_val:
                changes.append(f'{k}: "{old_val}" → "{new_val}"')
    if changes:
        db.log_activity('update_student', f'Aluno editado: {s["name"]} ({s["enrollment"]}) — {", ".join(changes)}', session.get('user_id'))
    return jsonify({'ok': True, 'student': s})


@bp.route('/api/students/<int:sid>', methods=['DELETE'])
@admin_required
def delete_student(sid):
    s = db.get_student(sid)
    if not s: return jsonify({'error': 'Não encontrado'}), 404
    if s.get('active_loans', 0) > 0:
        return jsonify({'error': 'Aluno possui empréstimos ativos'}), 400
    db.deactivate_student(sid)
    db.log_activity('delete_student', f'Aluno removido: {s["name"]} ({s["enrollment"]})', session.get('user_id'))
    return jsonify({'ok': True})


@bp.route('/api/students/<int:sid>/toggle-active', methods=['POST'])
@auth_required
def toggle_student_active(sid):
    if not has_operator_permission('can_edit_students'):
        return jsonify({'error': 'Permissao negada'}), 403
    s = db.get_student(sid)
    if not s: return jsonify({'error': 'Não encontrado'}), 404
    new_active = 0 if s.get('active', 1) else 1
    if not new_active and s.get('active_loans', 0) > 0:
        return jsonify({'error': 'Aluno possui empréstimos ativos — não pode ser desativado'}), 400
    db.set_student_active(sid, new_active)
    if not new_active:
        services.cancel_student_reservations(sid)
    status = 'reativado' if new_active else 'desativado'
    db.log_activity('update_student', f'Aluno {status}: {s["name"]} ({s["enrollment"]})', session.get('user_id'))
    return jsonify({'ok': True, 'active': new_active})


@bp.route('/api/students/by-class/<class_name>')
@auth_required
def get_students_by_class(class_name):
    return jsonify(db.get_students_by_class(class_name))


@bp.route('/api/students/batch-update-class', methods=['POST'])
@auth_required
def batch_update_class():
    if not has_operator_permission('can_edit_students'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    changes = data.get('changes', [])
    if not changes:
        return jsonify({'error': 'Nenhuma alteracao'}), 400
    count = db.batch_update_class(changes)
    db.log_activity('batch_update_class', f'Turmas atualizadas: {count} alunos', session.get('user_id'))
    return jsonify({'ok': True, 'count': count})


@bp.route('/api/students/deactivate-class', methods=['POST'])
@auth_required
def deactivate_class():
    if not has_operator_permission('can_edit_students'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    class_name = (data.get('class_name') or '').strip()
    if not class_name:
        return jsonify({'error': 'Informe a turma'}), 400
    count = db.deactivate_class(class_name)
    db.log_activity('deactivate_class', f'Turma {class_name} desativada: {count} alunos', session.get('user_id'))
    return jsonify({'ok': True, 'count': count})


@bp.route('/api/students/import-csv', methods=['POST'])
@auth_required
def import_students_csv():
    import csv, io
    file = request.files.get('file')
    if not file: return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    content = file.read().decode('utf-8-sig', errors='replace')
    reader = csv.DictReader(io.StringIO(content))
    imported, skipped, errors = 0, 0, []
    for i, row in enumerate(reader, 1):
        try:
            enrollment = (row.get('matricula') or row.get('matrícula') or row.get('enrollment') or '').strip()
            name = (row.get('nome') or row.get('name') or '').strip()
            if not enrollment or not name: errors.append(f'Linha {i+1}: matrícula ou nome vazio'); skipped += 1; continue
            if db.get_student_by_enrollment(enrollment): skipped += 1; continue
            db.create_student({'name': name, 'enrollment': enrollment,
                               'class_name': (row.get('turma') or row.get('class') or '').strip(),
                               'phone': (row.get('telefone') or row.get('phone') or '').strip(),
                               'email': (row.get('email') or '').strip()})
            imported += 1
        except Exception as e:
            errors.append(f'Linha {i+1}: {e}')
    db.log_activity('import_students', f'CSV: {imported} alunos importados, {skipped} ignorados', session.get('user_id'))
    return jsonify({'ok': True, 'imported': imported, 'skipped': skipped, 'errors': errors[:10]})
