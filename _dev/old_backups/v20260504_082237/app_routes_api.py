from flask import Blueprint, request, jsonify
from .. import database as db
from .. import version_control as vc
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


@bp.route('/api/version/create', methods=['POST'])
@auth_required
def create_version():
    if not has_operator_permission('can_manage_settings'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json() or {}
    description = data.get('description', 'Manual backup')
    try:
        version_id = vc.create_version(description)
        return jsonify({'success': True, 'version_id': version_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/version/list')
@auth_required
def list_versions():
    if not has_operator_permission('can_manage_settings'):
        return jsonify({'error': 'Permissao negada'}), 403
    versions = vc.list_versions()
    return jsonify({'versions': versions})


@bp.route('/api/version/rollback', methods=['POST'])
@auth_required
def rollback_version():
    if not has_operator_permission('can_manage_settings'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json() or {}
    version_id = data.get('version_id')
    if not version_id:
        return jsonify({'error': 'version_id required'}), 400
    try:
        vc.rollback_to_version(version_id)
        return jsonify({'success': True, 'message': f'Rollback to {version_id} completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/version/current')
@auth_required
def get_current_version():
    current = vc.get_current_version()
    return jsonify({'current_version': current})
