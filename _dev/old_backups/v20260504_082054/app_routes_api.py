from flask import Blueprint, request, jsonify
from .. import database as db
from .auth import auth_required
from .settings import has_operator_permission

bp = Blueprint('api', __name__)


@bp.route('/api/activity')
@auth_required
def get_activity():
    if not has_operator_permission('can_view_activity'):
        return jsonify({'error': 'Permissao negada'}), 403
    return jsonify(db.list_activity(50))


@bp.route('/api/search')
@auth_required
def global_search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'books': [], 'students': []})
    return jsonify(db.global_search(q))
