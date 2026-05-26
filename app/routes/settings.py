from flask import Blueprint, request, jsonify, session, send_file, current_app, render_template
from datetime import datetime
import os, sys, shutil, sqlite3, time, threading, subprocess
from .. import database as db
from ..version import VERSION
from .auth import auth_required, admin_required

bp = Blueprint('settings', __name__)


@bp.route('/instituicao')
@admin_required
def institution_page():
    inst = db.get_institution()
    return render_template('app.html', page='institution', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/categorias')
@auth_required
def categories_page():
    inst = db.get_institution()
    return render_template('app.html', page='categories', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/permissoes')
@admin_required
def permissions_page():
    inst = db.get_institution()
    return render_template('app.html', page='permissions', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/institution', methods=['GET'])
@auth_required
def get_institution():
    return jsonify(db.get_institution() or {})


@bp.route('/api/institution/loan-days')
@auth_required
def get_loan_days_default():
    inst = db.get_institution()
    return jsonify({'loan_days_default': (inst or {}).get('loan_days_default', 14)})


@bp.route('/api/institution', methods=['PUT'])
@admin_required
def update_institution():
    db.update_institution(request.get_json())
    return jsonify({'ok': True})


@bp.route('/usuarios')
@auth_required
def users_page():
    inst = db.get_institution()
    return render_template('app.html', page='users', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/users', methods=['GET'])
@auth_required
def get_users():
    return jsonify(db.list_users())


@bp.route('/api/users', methods=['POST'])
@auth_required
def create_user():
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Apenas administradores podem criar usuários'}), 403
    data = request.get_json()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not name or not email or not password:
        return jsonify({'error': 'Nome, e-mail e senha são obrigatórios'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Senha deve ter ao menos 6 caracteres'}), 400
    if db.get_user_by_email(email):
        return jsonify({'error': 'E-mail já cadastrado'}), 400
    u = db.create_user({**data, 'name': name, 'email': email})
    db.log_activity('create_user', f'Usuário criado: {name} ({email})', session.get('user_id'))
    return jsonify({'ok': True, 'user': u})


@bp.route('/api/users/<int:uid>', methods=['PUT'])
@auth_required
def update_user(uid):
    if session.get('user_role') != 'admin' and session.get('user_id') != uid:
        return jsonify({'error': 'Acesso negado'}), 403
    data = request.get_json()
    if data.get('password') and len(data['password']) < 6:
        return jsonify({'error': 'Senha deve ter ao menos 6 caracteres'}), 400
    db.update_user(uid, data)
    return jsonify({'ok': True})


@bp.route('/api/users/<int:uid>', methods=['DELETE'])
@admin_required
def delete_user(uid):
    if uid == session.get('user_id'):
        return jsonify({'error': 'Não pode excluir sua própria conta'}), 400
    db.deactivate_user(uid)
    return jsonify({'ok': True})


@bp.route('/api/users/change-password', methods=['POST'])
@auth_required
def change_own_password():
    data = request.get_json()
    uid = session['user_id']
    if not db.check_user_password(uid, data.get('current_password', '')):
        return jsonify({'error': 'Senha atual incorreta'}), 400
    new_pw = data.get('new_password', '')
    if len(new_pw) < 6:
        return jsonify({'error': 'Nova senha deve ter ao menos 6 caracteres'}), 400
    db.change_user_password(uid, new_pw)
    return jsonify({'ok': True})


@bp.route('/backup')
@auth_required
def backup_page():
    inst = db.get_institution()
    return render_template('app.html', page='backup', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/limpeza')
@admin_required
def cleanup_page():
    inst = db.get_institution()
    return render_template('app.html', page='cleanup', institution=inst,
                           user_name=session.get('user_name'), user_role=session.get('user_role'))


@bp.route('/api/backup/download')
@auth_required
def download_backup():
    if not has_operator_permission('can_backup'):
        return jsonify({'error': 'Permissao negada'}), 403
    db_path = current_app.config['DB_PATH']
    backup_dir = current_app.config['BACKUP_DIR']
    # Checkpoint WAL to ensure all data is in main db file
    with db.get_conn() as conn:
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'biblioteca_backup_{ts}.db'
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(db_path, backup_path)
    db.log_activity('backup', f'Backup: {backup_name}', session.get('user_id'))
    return send_file(backup_path, as_attachment=True, download_name=backup_name)


def _find_rclone():
    """Procura rclone no PATH e na pasta do executável."""
    rclone = shutil.which('rclone')
    if rclone:
        return rclone
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else None
    if exe_dir:
        candidate = os.path.join(exe_dir, 'rclone.exe') if sys.platform == 'win32' else os.path.join(exe_dir, 'rclone')
        if os.path.exists(candidate):
            return candidate
    return None


@bp.route('/api/backup/cloud-status')
@auth_required
def cloud_backup_status():
    """Verifica se rclone está instalado e configurado."""
    rclone = _find_rclone()
    if not rclone:
        return jsonify({'available': False, 'reason': 'not_installed',
                        'message': 'rclone não encontrado. Instale em https://rclone.org'})
    try:
        result = subprocess.run([rclone, 'listremotes'], capture_output=True, text=True, timeout=10)
        remotes = [r.strip().rstrip(':') for r in result.stdout.strip().split('\n') if r.strip()]
        if not remotes:
            return jsonify({'available': False, 'reason': 'not_configured',
                            'message': 'rclone instalado mas sem remotes configurados. Execute: rclone config'})
        return jsonify({'available': True, 'remotes': remotes})
    except subprocess.TimeoutExpired:
        return jsonify({'available': False, 'reason': 'timeout', 'message': 'rclone não respondeu'})
    except Exception as e:
        return jsonify({'available': False, 'reason': 'error', 'message': str(e)})


@bp.route('/api/backup/cloud-upload', methods=['POST'])
@auth_required
def cloud_backup_upload():
    """Envia backup para a nuvem via rclone."""
    if not has_operator_permission('can_backup'):
        return jsonify({'error': 'Permissao negada'}), 403
    rclone = _find_rclone()
    if not rclone:
        return jsonify({'error': 'rclone não instalado'}), 400
    remote = request.json.get('remote', '')
    if not remote:
        return jsonify({'error': 'Informe o remote'}), 400
    db_path = current_app.config['DB_PATH']
    backup_dir = current_app.config['BACKUP_DIR']
    with db.get_conn() as conn:
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'biblioteca_backup_{ts}.db'
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(db_path, backup_path)
    try:
        result = subprocess.run(
            [rclone, 'copy', backup_path, f'{remote}:Biblioteca/backups/'],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            db.log_activity('backup', f'Backup enviado para nuvem ({remote}): {backup_name}',
                            session.get('user_id'))
            return jsonify({'ok': True, 'message': 'Backup enviado para nuvem com sucesso'})
        else:
            return jsonify({'ok': False, 'error': result.stderr.strip()}), 500
    except subprocess.TimeoutExpired:
        return jsonify({'ok': False, 'error': 'Tempo limite excedido (2 min)'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@bp.route('/api/backup/restore', methods=['POST'])
@admin_required
def restore_backup():
    try:
        file = request.files.get('file')
        if not file or not file.filename.endswith('.db'):
            return jsonify({'error': 'Arquivo .db invalido'}), 400
        db_path = current_app.config['DB_PATH']
        backup_dir = current_app.config['BACKUP_DIR']
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Fazer backup antes de restaurar
        if os.path.exists(db_path):
            shutil.copy2(db_path, os.path.join(backup_dir, f'pre_restore_{ts}.db'))
        # Salvar arquivo temporariamente primeiro
        temp_path = db_path + '.temp'
        file.save(temp_path)
        # Verificar se é um banco SQLite válido
        try:
            test_conn = sqlite3.connect(temp_path)
            test_conn.execute("PRAGMA integrity_check").fetchone()
            # Verificar se todas as tabelas necessárias existem
            tables = [r[0] for r in test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            required_tables = ['institution', 'users', 'books', 'students', 'loans', 'activity_log', 'license_info', 'categories', 'operator_permissions']
            missing = [t for t in required_tables if t not in tables]
            test_conn.close()
            if missing:
                os.remove(temp_path)
                return jsonify({'error': f'Backup inválido: faltam tabelas ({", ".join(missing)})'}), 400
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': f'Arquivo de backup inválido ou corrompido: {str(e)}'}), 400
        # Substituir banco atual
        if os.path.exists(db_path):
            os.replace(temp_path, db_path)
        else:
            os.rename(temp_path, db_path)
        wal = db_path + '-wal'
        shm = db_path + '-shm'
        if os.path.exists(wal): os.remove(wal)
        if os.path.exists(shm): os.remove(shm)
        return jsonify({'ok': True, 'message': 'Banco restaurado com sucesso. Reinicie o sistema para aplicar as alteracoes.'})
    except Exception as e:
        import logging
        logging.error(f"Erro em restore_backup: {e}", exc_info=True)
        return jsonify({'error': f'Erro ao restaurar backup: {str(e)}'}), 500


@bp.route('/api/backup/restore-by-name', methods=['POST'])
@admin_required
def restore_backup_by_name():
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'Nome do backup obrigatorio'}), 400
        backup_dir = current_app.config['BACKUP_DIR']
        src = os.path.join(backup_dir, name)
        if not os.path.exists(src):
            return jsonify({'error': 'Backup nao encontrado'}), 404
        db_path = current_app.config['DB_PATH']
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        if os.path.exists(db_path):
            shutil.copy2(db_path, os.path.join(backup_dir, f'pre_restore_{ts}.db'))
        shutil.copy2(src, db_path)
        wal = db_path + '-wal'
        shm = db_path + '-shm'
        if os.path.exists(wal): os.remove(wal)
        if os.path.exists(shm): os.remove(shm)
        return jsonify({'ok': True, 'message': 'Banco restaurado com sucesso.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/backup/list')
@auth_required
def list_backups():
    try:
        backup_dir = current_app.config['BACKUP_DIR']
        files = []
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.endswith('.db'):
                    fp = os.path.join(backup_dir, f)
                    try:
                        files.append({'name': f, 'size_kb': round(os.path.getsize(fp)/1024, 1),
                                      'date': datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%d/%m/%Y %H:%M'),
                                      'mtime': os.path.getmtime(fp)})
                    except:
                        pass
            files.sort(key=lambda x: x['mtime'], reverse=True)
        return jsonify({'files': files[:3], 'dir': backup_dir})
    except Exception as e:
        import logging
        logging.error(f"Erro em list_backups: {e}", exc_info=True)
        return jsonify([])


@bp.route('/api/system/shutdown', methods=['POST'])
@auth_required
def shutdown_system():
    """Cria backup e encerra o servidor."""
    try:
        backup_dir = current_app.config['BACKUP_DIR']
        db_path = current_app.config['DB_PATH']
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'biblioteca_backup_exit_{ts}.db'
        backup_path = os.path.join(backup_dir, backup_name)
        
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(db_path, backup_path)
        db.log_activity('backup', f'Backup de saída: {backup_name}', session.get('user_id'))
        
        # Resposta para o cliente fechar a janela
        resp = jsonify({'ok': True, 'backup': backup_name})
        
        # Agenda o shutdown após enviar a resposta
        def do_shutdown():
            time.sleep(1)
            os._exit(0)
        threading.Thread(target=do_shutdown, daemon=True).start()
        
        return resp
    except Exception as e:
        logging.error(f"Erro no shutdown: {e}", exc_info=True)
        # Se falhar o backup, ainda permite sair? Melhor não.
        return jsonify({'error': f'Erro ao criar backup: {str(e)}'}), 500


@bp.route('/api/institution/logo', methods=['POST'])
@admin_required
def upload_logo():
    file = request.files.get('logo')
    if not file:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.svg'):
        return jsonify({'error': 'Formato inválido. Use PNG, JPG, GIF ou SVG.'}), 400
    logo_dir = os.path.join(current_app.config['BASE_DIR'], 'instance', 'logos')
    os.makedirs(logo_dir, exist_ok=True)
    logo_filename = f'institution_logo{ext}'
    logo_path = os.path.join(logo_dir, logo_filename)
    file.save(logo_path)
    db.update_institution_logo(logo_path)
    db.log_activity('update_institution', 'Logo da instituição atualizado', session.get('user_id'))
    return jsonify({'ok': True, 'logo_path': f'/api/institution/logo-file?t={int(datetime.now().timestamp())}'})


@bp.route('/api/institution/logo-file')
@auth_required
def get_logo_file():
    inst = db.get_institution()
    logo_path = (inst or {}).get('logo_path', '')
    if not logo_path or not os.path.exists(logo_path):
        return '', 404
    return send_file(logo_path)


@bp.route('/api/categories', methods=['GET'])
@auth_required
def get_categories_list():
    return jsonify(db.list_categories())


@bp.route('/api/categories', methods=['POST'])
@auth_required
def create_category():
    if not has_operator_permission('can_manage_categories'):
        return jsonify({'error': 'Permissao negada'}), 403
    data = request.get_json()
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    existing = db.list_categories()
    if any(c['name'].lower() == name.lower() for c in existing):
        return jsonify({'error': 'Categoria já existe'}), 400
    cat = db.create_category(name)
    db.log_activity('create_category', f'Categoria criada: {name}', session.get('user_id'))
    return jsonify({'ok': True, 'category': cat})


@bp.route('/api/categories/<int:cid>', methods=['DELETE'])
@auth_required
def delete_category(cid):
    if not has_operator_permission('can_manage_categories'):
        return jsonify({'error': 'Permissao negada'}), 403
    db.delete_category(cid)
    return jsonify({'ok': True})


@bp.route('/api/books/import-template')
@auth_required
def books_import_template():
    import io
    content = 'patrimonio,titulo,autor,isbn,categoria,editora,ano\nPAT-00001,Exemplo de Livro,Autor Exemplo,978-0-00-000000-1,Romance,Editora X,2024'
    return send_file(io.BytesIO(content.encode('utf-8-sig')), mimetype='text/csv',
                     as_attachment=True, download_name='template_livros.csv')


@bp.route('/api/students/import-template')
@auth_required
def students_import_template():
    import io
    content = 'matricula,nome,turma,telefone,email\n2026001,Aluno Exemplo,9A,(00) 00000-0000,aluno@email.com'
    return send_file(io.BytesIO(content.encode('utf-8-sig')), mimetype='text/csv',
                     as_attachment=True, download_name='template_alunos.csv')


@bp.route('/api/operator-permissions')
@auth_required
def get_operator_permissions():
    return jsonify(db.get_operator_permissions())


@bp.route('/api/operator-permissions', methods=['POST'])
@admin_required
def save_operator_permissions():
    data = request.get_json()
    db.save_operator_permissions(data)
    db.log_activity('update_permissions', 'Permissoes do operador atualizadas', session.get('user_id'))
    return jsonify({'ok': True})


@bp.route('/api/version')
@auth_required
def get_version():
    lic = db.get_license()
    inst = db.get_institution()
    return jsonify({
        'version': VERSION,
        'institution': (inst or {}).get('name', ''),
        'desenvolvido_por': 'Rafael David',
        'license_valid_until': (lic or {}).get('valid_until', ''),
        'license_active': bool(lic and lic.get('is_valid'))
    })


def has_operator_permission(perm):
    if session.get('user_role') == 'admin':
        return True
    perms = db.get_operator_permissions()
    return bool(perms.get(perm, False))


def operator_perm_required(perm):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not has_operator_permission(perm):
                return jsonify({'error': 'Permissao negada'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@bp.route('/api/cleanup', methods=['POST'])
@admin_required
def cleanup_data():
    import shutil
    from datetime import datetime
    data = request.get_json() or {}
    tables = data.get('tables', [])
    allowed = {'books', 'students', 'loans', 'activity_log', 'categories'}
    tables = [t for t in tables if t in allowed]
    if not tables:
        return jsonify({'error': 'Nenhuma tabela valida selecionada'}), 400
    db_path = current_app.config['DB_PATH']
    backup_dir = current_app.config['BACKUP_DIR']
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'pre_cleanup_{ts}.db'
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(db_path, backup_path)
    try:
        with db.get_conn() as conn:
            conn.execute('PRAGMA foreign_keys = OFF')
            for table in tables:
                conn.execute(f'DELETE FROM {table}')
            conn.execute('PRAGMA foreign_keys = ON')
            conn.commit()
            conn.execute('VACUUM')
    except Exception as e:
        import logging
        logging.error(f"Erro em cleanup_data: {e}", exc_info=True)
        return jsonify({'error': f'Erro ao limpar dados: {str(e)}'}), 500
    db.log_activity('cleanup', f'Limpeza de dados: {", ".join(tables)}', session.get('user_id'))
    return jsonify({'ok': True, 'backup': backup_name, 'tables': tables})
