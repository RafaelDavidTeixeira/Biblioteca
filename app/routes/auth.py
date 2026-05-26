from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from functools import wraps
import logging
from .. import database as db
from ..license import get_machine_id, validate_license_key

bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def _is_api():
    """Retorna True se a requisição é para uma rota /api/ (deve responder JSON)"""
    return request.path.startswith('/api/')


def license_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            if not db.is_license_valid():
                logging.warning("Licença inválida ou expirada")
                if _is_api():
                    return jsonify({'ok': False, 'error': 'Licença inativa. Ative o sistema para continuar.', 'license_inactive': True}), 403
                return redirect(url_for('auth.license_check'))
        except Exception as e:
            logging.error(f"Erro ao verificar licença: {e}", exc_info=True)
            if _is_api():
                return jsonify({'ok': False, 'error': f'Erro na verificação de licença: {str(e)}', 'license_inactive': True}), 403
            return redirect(url_for('auth.license_check'))
        return f(*args, **kwargs)
    return decorated


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1º verifica login, 2º verifica licença
        if 'user_id' not in session:
            if _is_api():
                return jsonify({'ok': False, 'error': 'Não autenticado'}), 401
            return redirect(url_for('auth.login'))
        try:
            if not db.is_license_valid():
                logging.warning("Licença inválida ou expirada")
                if _is_api():
                    return jsonify({'ok': False, 'error': 'Licença inativa. Ative o sistema para continuar.', 'license_inactive': True}), 403
                return redirect(url_for('auth.license_check'))
        except Exception as e:
            logging.error(f"Erro ao verificar licença: {e}", exc_info=True)
            if _is_api():
                return jsonify({'ok': False, 'error': f'Erro na verificação de licença: {str(e)}', 'license_inactive': True}), 403
            return redirect(url_for('auth.license_check'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if _is_api():
                return jsonify({'ok': False, 'error': 'Não autenticado'}), 401
            return redirect(url_for('auth.login'))
        try:
            if not db.is_license_valid():
                if _is_api():
                    return jsonify({'ok': False, 'error': 'Licença inativa.', 'license_inactive': True}), 403
                return redirect(url_for('auth.license_check'))
        except Exception as e:
            if _is_api():
                return jsonify({'ok': False, 'error': str(e), 'license_inactive': True}), 403
            return redirect(url_for('auth.license_check'))
        if session.get('user_role') != 'admin':
            return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
        return f(*args, **kwargs)
    return decorated


@bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('books.dashboard'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    machine_id = get_machine_id()
    # Check if license is valid AND not expired
    license_ok = db.is_license_valid()

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        identifier = (data.get('email') or data.get('identifier') or '').strip()
        password = data.get('password') or ''

        user = db.get_user_by_login_identifier(identifier)
        if user and db.check_user_password(user['id'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            db.update_last_login(user['id'])
            db.log_activity('login', f'Login: {user["name"]}', user['id'])
            if request.is_json:
                return jsonify({'ok': True})
            return redirect(url_for('books.dashboard'))

        if request.is_json:
            return jsonify({'ok': False, 'error': 'Identificador ou senha incorretos'}), 401
        return render_template('login.html', error='Identificador ou senha incorretos',
                               machine_id=machine_id, license_ok=license_ok)

    return render_template('login.html', machine_id=machine_id, license_ok=license_ok)


@bp.route('/license-check')
@login_required
def license_check():
    from datetime import date
    inst = db.get_institution()
    machine_id = get_machine_id()
    
    # Get detailed license info for template
    lic = db.get_license()
    license_ok = db.is_license_valid()
    
    # Get expiration date for display
    valid_until_br = ''
    days_left = None
    if lic and lic.get('valid_until'):
        try:
            valid_until_str = lic.get('valid_until')
            if '-' in valid_until_str:
                parts = valid_until_str.split('-')
                valid_until = date(int(parts[0]), int(parts[1]), int(parts[2]))
                valid_until_br = valid_until.strftime('%d/%m/%Y')
                days_left = (valid_until - date.today()).days
            elif '/' in valid_until_str:
                parts = valid_until_str.split('/')
                valid_until = date(int(parts[2]), int(parts[1]), int(parts[0]))
                valid_until_br = valid_until.strftime('%d/%m/%Y')
                days_left = (valid_until - date.today()).days
        except:
            pass
    
    return render_template('app.html', page='license_check', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'),
                           machine_id=machine_id, license_ok=license_ok,
                           valid_until_br=valid_until_br, days_left=days_left)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/api/license/activate', methods=['POST'])
def activate_license():
    data = request.get_json()
    key = (data.get('key') or '').strip()
    institution = (data.get('institution') or 'Instituição').strip()
    machine_id = get_machine_id()
    result = validate_license_key(key, machine_id)
    if result['valid']:
        db.save_license(machine_id, key, institution, result['valid_until_date'])
        return jsonify({'ok': True, 'institution': institution, 'valid_until': result['valid_until']})
    return jsonify({'ok': False, 'error': result['error']}), 400


@bp.route('/api/license/status')
def license_status():
    from datetime import date
    machine_id = get_machine_id()
    
    # Use the same validation as is_license_valid()
    is_valid = db.is_license_valid()
    
    response = {
        'machine_id': machine_id,
        'active': is_valid
    }
    
    if is_valid:
        lic = db.get_license()
        valid_until_str = lic.get('valid_until')
        try:
            if '-' in valid_until_str:
                parts = valid_until_str.split('-')
                valid_until = date(int(parts[0]), int(parts[1]), int(parts[2]))
            elif '/' in valid_until_str:
                parts = valid_until_str.split('/')
                valid_until = date(int(parts[2]), int(parts[1]), int(parts[0]))
            else:
                valid_until = None
            
            if valid_until:
                days_left = (valid_until - date.today()).days
                response['institution'] = lic.get('institution_name')
                response['valid_until'] = valid_until.isoformat()
                response['valid_until_br'] = valid_until.strftime('%d/%m/%Y')
                response['days_left'] = days_left
                response['expired'] = days_left < 0
        except Exception as e:
            print(f"Error parsing license date: {e}")
    
    return jsonify(response)
