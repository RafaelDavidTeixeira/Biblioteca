import os
import sys
from flask import Flask, send_file
from . import database as db


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        os.chdir(base_dir)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(base_dir, 'instance', 'biblioteca.db')

    app.config['SECRET_KEY'] = 'biblioteca-secret-2026-xK9mP3'
    app.config['BASE_DIR'] = base_dir
    app.config['BACKUP_DIR'] = os.path.join(base_dir, 'backups')
    app.config['DB_PATH'] = db_path

    os.makedirs(app.config['BACKUP_DIR'], exist_ok=True)
    os.makedirs(instance_dir, exist_ok=True)

    db.init_db(db_path)

    from .routes import auth, books, students, loans, reports, settings, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(students.bp)
    app.register_blueprint(loans.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(api.bp)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        if path and (path.startswith('api/') or path.startswith('static/')):
            return {'error': 'Not Found'}, 404
        return send_file(os.path.join(base_dir, 'app', 'templates', 'app.html'))

    return app
