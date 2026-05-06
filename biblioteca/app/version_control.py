import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

VERSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'versions.json')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'backups')

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_versions():
    """Load version history from JSON file"""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'current_version': None, 'versions': []}

def save_versions(data):
    """Save version history to JSON file"""
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_version(description, files_to_backup=None):
    """Create a new version with backup of specified files"""
    if files_to_backup is None:
        files_to_backup = [
            'app/templates/app.html',
            'app/__init__.py',
            'app/routes/auth.py',
            'app/routes/api.py',
            'app/routes/books.py',
            'app/routes/students.py',
            'app/routes/loans.py',
        ]
    
    data = load_versions()
    version_id = datetime.now().strftime('v%Y%m%d_%H%M%S')
    
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    version_backup_dir = os.path.join(BACKUP_DIR, version_id)
    os.makedirs(version_backup_dir, exist_ok=True)
    
    backed_up_files = []
    for filepath in files_to_backup:
        src = os.path.join(base_dir, filepath)
        if os.path.exists(src):
            dst = os.path.join(version_backup_dir, filepath.replace('/', '_'))
            shutil.copy2(src, dst)
            backed_up_files.append({
                'original_path': filepath,
                'backup_path': dst,
                'hash': get_file_hash(src)
            })
    
    version_info = {
        'id': version_id,
        'timestamp': datetime.now().isoformat(),
        'description': description,
        'files': backed_up_files
    }
    
    data['versions'].append(version_info)
    data['current_version'] = version_id
    save_versions(data)
    
    return version_id

def rollback_to_version(version_id):
    """Rollback to a specific version"""
    data = load_versions()
    version_info = None
    
    for v in data['versions']:
        if v['id'] == version_id:
            version_info = v
            break
    
    if not version_info:
        raise ValueError(f'Version {version_id} not found')
    
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    for file_info in version_info['files']:
        backup_path = file_info['backup_path']
        original_path = os.path.join(base_dir, file_info['original_path'])
        
        if os.path.exists(backup_path):
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            shutil.copy2(backup_path, original_path)
    
    data['current_version'] = version_id
    save_versions(data)
    
    return True

def list_versions():
    """List all available versions"""
    data = load_versions()
    return data['versions']

def get_current_version():
    """Get current version ID"""
    data = load_versions()
    return data.get('current_version')
