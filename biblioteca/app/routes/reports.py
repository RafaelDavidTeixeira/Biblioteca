from flask import Blueprint, request, jsonify, session, render_template
from .. import database as db
from .auth import auth_required

bp = Blueprint('reports', __name__)


@bp.route('/relatorios')
@auth_required
def reports_page():
    inst = db.get_institution()
    return render_template('app.html', page='reports', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/reports/active-loans')
@auth_required
def report_active_loans():
    return jsonify(db.report_active_loans(request.args.get('class_name', '')))


@bp.route('/api/reports/overdue')
@auth_required
def report_overdue():
    return jsonify(db.report_overdue(request.args.get('class_name', '')))


@bp.route('/api/reports/student-history')
@auth_required
def report_student_history():
    sid = request.args.get('student_id')
    if not sid: return jsonify({'error': 'Aluno obrigatório'}), 400
    return jsonify(db.report_student_history(int(sid), request.args.get('date_from', ''), request.args.get('date_to', '')))


@bp.route('/api/reports/movement')
@auth_required
def report_movement():
    return jsonify(db.report_movement(request.args.get('date_from', ''), request.args.get('date_to', ''), request.args.get('type', 'all')))


@bp.route('/api/reports/inventory')
@auth_required
def report_inventory():
    return jsonify(db.report_inventory(request.args.get('category', ''), request.args.get('status', '')))


@bp.route('/api/reports/most-borrowed')
@auth_required
def report_most_borrowed():
    return jsonify(db.report_most_borrowed(request.args.get('date_from', ''), request.args.get('date_to', ''), request.args.get('category', '')))


@bp.route('/api/reports/classes')
@auth_required
def get_classes():
    return jsonify(db.get_classes())

@bp.route('/api/reports/student-ranking')
@auth_required
def report_student_ranking():
    try:
        return jsonify(db.report_student_ranking(
            request.args.get('date_from', ''),
            request.args.get('date_to', ''),
            request.args.get('class_name', ''),
            request.args.get('student_id', ''),
            request.args.get('min_loans', 0)
        ))
    except Exception as e:
        import logging, traceback
        logging.error(f"Erro student-ranking: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/reports/class-ranking')
@auth_required
def report_class_ranking():
    try:
        return jsonify(db.report_class_ranking(
            request.args.get('date_from', ''),
            request.args.get('date_to', '')
        ))
    except Exception as e:
        import logging, traceback
        logging.error(f"Erro class-ranking: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/reports/categories')
@auth_required
def get_categories():
    return jsonify(db.get_categories())
