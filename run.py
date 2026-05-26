"""
Biblioteca - Sistema de Controle de Acervo
Entry point: run.py
"""
import sys
import os
import atexit
import shutil
import threading
import time
from datetime import datetime

# IMPORTANTE: forçar resolução do pacote 'app' local ANTES de qualquer import
# Necessário para evitar conflito com módulos externos no Python 3.14+
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

# Remover entradas que possam conter um 'app' externo conflitante
sys.path = [p for p in sys.path if 'site-packages' not in p or
            not os.path.exists(os.path.join(p, 'app', '__init__.py'))]
sys.path.insert(0, _BASE_DIR)

# When frozen by PyInstaller, use APPDATA on Windows to avoid admin rights
if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(sys.executable)
    if sys.platform == 'win32':
        BASE_DIR = os.path.join(os.environ.get('APPDATA', EXE_DIR), 'Biblioteca')
    else:
        BASE_DIR = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'Biblioteca')
    os.makedirs(BASE_DIR, exist_ok=True)
    os.chdir(BASE_DIR)
else:
    BASE_DIR = _BASE_DIR

import logging
from app import create_app

PORT = 5477
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DB_PATH = os.path.join(BASE_DIR, 'instance', 'biblioteca.db')

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def auto_backup():
    """Cria backup automático do banco de dados ao encerrar."""
    try:
        if os.path.exists(DB_PATH):
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'biblioteca_backup_{timestamp}.db'
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            
            # Tenta copiar. Se falhar por estar travado, tenta de novo rapidamente.
            try:
                shutil.copy2(DB_PATH, backup_path)
                logging.info(f"Backup automático criado: {backup_name}")
            except Exception as e:
                logging.warning(f"Backup automático falhou na primeira tentativa: {e}")
                time.sleep(0.5)
                shutil.copy2(DB_PATH, backup_path)
                logging.info(f"Backup automático criado (tentativa 2): {backup_name}")
                
            # Limpeza: manter apenas os últimos 10 backups automáticos
            backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('biblioteca_backup_')], reverse=True)
            for old in backups[10:]:
                os.remove(os.path.join(BACKUP_DIR, old))
    except Exception as e:
        logging.error(f"Erro no backup automático: {e}")

# Registrar o backup para rodar na saída do programa
atexit.register(auto_backup)

def _kill_existing_server():
    """Mata qualquer servidor existente na porta antes de iniciar."""
    import subprocess
    port = str(PORT)
    if sys.platform == 'win32':
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.splitlines():
                line = line.strip()
                if f'127.0.0.1:{port}' in line and 'LISTENING' in line:
                    parts = [p for p in line.split() if p]
                    pid = parts[-1]
                    if pid.isdigit():
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, timeout=5)
                        time.sleep(0.5)
        except:
            pass
    else:
        try:
            result = subprocess.run(['fuser', f'{port}/tcp'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for pid in result.stdout.strip().split():
                    subprocess.run(['kill', '-9', pid], capture_output=True, timeout=3)
                time.sleep(0.5)
        except:
            pass

def open_browser():
    import subprocess, socket, shutil, logging
    url = 'http://127.0.0.1:{}'.format(PORT)
    try:
        with open(os.path.join(BASE_DIR, 'url.txt'), 'w') as f:
            f.write('Biblioteca - Acesse: {}\n'.format(url))
    except:
        pass
    for _ in range(60):
        try:
            s = socket.create_connection(('127.0.0.1', PORT), timeout=1)
            s.close()
            break
        except:
            time.sleep(0.5)
    logging.info('Abrindo navegador: {}'.format(url))
    _try_open_browser(url)

def _try_open_browser(url):
    import subprocess, logging

    devnull = subprocess.DEVNULL

    # Verifica se há display disponível
    has_display = bool(
        os.environ.get('DISPLAY') or
        os.environ.get('WAYLAND_DISPLAY') or
        sys.platform == 'win32' or
        sys.platform == 'darwin'
    )
    if not has_display:
        logging.warning('Sem display detectado. Acesse manualmente: {}'.format(url))
        print('\n  >>> Acesse no navegador: {} <<<\n'.format(url))
        return

    if sys.platform == 'win32':
        try:
            os.startfile(url)
            logging.info('Navegador aberto via os.startfile')
            return
        except Exception as e:
            logging.warning('os.startfile falhou: {}'.format(e))
        return

    # Linux/Mac: usa script shell externo completamente desacoplado do AppImage.
    # Isso contorna o problema do AppImage isolar o PATH e o ambiente, impedindo
    # que shutil.which() encontre os browsers instalados no sistema.
    script = (
        'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin:"$PATH"\n'
        'export DISPLAY="${DISPLAY:-:0}"\n'
        'for b in google-chrome-stable google-chrome firefox chromium-browser chromium brave-browser opera xdg-open; do\n'
        '  cmd=$(which "$b" 2>/dev/null)\n'
        '  if [ -n "$cmd" ]; then\n'
        '    "$cmd" --no-sandbox "' + url + '" >/dev/null 2>&1 &\n'
        '    exit 0\n'
        '  fi\n'
        'done\n'
    )
    try:
        subprocess.Popen(
            ['sh', '-c', script],
            stdout=devnull,
            stderr=devnull,
            stdin=devnull,
            start_new_session=True,
            close_fds=True
        )
        logging.info('Navegador aberto via script shell')
        return
    except Exception as e:
        logging.warning('script shell falhou: {}'.format(e))

    logging.warning('Nenhum browser encontrado. Acesse manualmente: {}'.format(url))
    print('\n  >>> Acesse no navegador: {} <<<\n'.format(url))

def main():
    _kill_existing_server()
    app = create_app()

    # Rota auxiliar para captura de screenshots
    @app.route('/_screen_login')
    def _screen_login():
        from flask import redirect as rd, request as rq, session as sess
        from app import database as db2
        user = db2.get_user_by_login_identifier('admin@biblioteca.local')
        if user:
            sess['user_id'] = user['id']
            sess['user_name'] = user['name']
            sess['user_role'] = user['role']
        return rd(rq.args.get('next', '/dashboard'))

    # Adicionar handler para erros 500
    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.error("Erro 500: {}".format(e), exc_info=True)
        from flask import jsonify
        return jsonify({'error': str(e), 'type': 'internal_error'}), 500

    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    print('')
    print('=' * 50)
    print('  Biblioteca - Sistema de Controle')
    print('  Acesse: http://127.0.0.1:{}'.format(PORT))
    print('  Login padrao: admin@biblioteca.local / admin123')
    print('  Pressione Ctrl+C para encerrar')
    print('=' * 50)
    print('')

    try:
        app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nSistema encerrado. Backup automático em execução...")
        auto_backup() # Força backup antes de sair no Ctrl+C
        sys.exit(0)

if __name__ == '__main__':
    main()
