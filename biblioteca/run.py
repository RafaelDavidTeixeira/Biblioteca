"""
Biblioteca - Sistema de Controle de Acervo
Entry point: run.py
"""
import sys
import os

# IMPORTANTE: forçar resolução do pacote 'app' local ANTES de qualquer import
# Necessário para evitar conflito com módulos externos no Python 3.14+
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

# Remover entradas que possam conter um 'app' externo conflitante
sys.path = [p for p in sys.path if 'site-packages' not in p or
            not os.path.exists(os.path.join(p, 'app', '__init__.py'))]
sys.path.insert(0, _BASE_DIR)

import threading
import webbrowser
import time

# When frozen by PyInstaller, fix paths
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    os.chdir(BASE_DIR)
else:
    BASE_DIR = _BASE_DIR

import logging
from app import create_app

PORT = 5477

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:{}'.format(PORT))

def main():
    app = create_app()

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
        print("\nSistema encerrado.")
        sys.exit(0)

if __name__ == '__main__':
    main()
