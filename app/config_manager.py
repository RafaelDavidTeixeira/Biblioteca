"""
Manages configuration values (secret keys, etc.) via instance/config.json.
Auto-generates on first run so secrets are never hardcoded.
"""
import os
import json
import secrets
import string

_CONFIG = None
_CONFIG_PATH = None


def _ensure_config(base_dir=None):
    global _CONFIG, _CONFIG_PATH
    if _CONFIG is not None:
        return _CONFIG
    if _CONFIG_PATH is None:
        if base_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        _CONFIG_PATH = os.path.join(base_dir, 'instance', 'config.json')
    if os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH, 'r') as f:
            _CONFIG = json.load(f)
        return _CONFIG
    _CONFIG = _generate_config()
    os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
    with open(_CONFIG_PATH, 'w') as f:
        json.dump(_CONFIG, f, indent=2)
    return _CONFIG


def _generate_config():
    alphabet = string.ascii_letters + string.digits
    return {
        'SECRET_KEY': ''.join(secrets.choice(alphabet) for _ in range(48)),
        'LICENSE_SECRET': 'biblio-lic-' + ''.join(secrets.choice(alphabet) for _ in range(16)),
        'created_at': None
    }


def get_secret_key(base_dir=None):
    cfg = _ensure_config(base_dir)
    return cfg.get('SECRET_KEY', 'fallback-dev-key')


def get_license_secret(base_dir=None):
    cfg = _ensure_config(base_dir)
    return cfg.get('LICENSE_SECRET', 'biblio-lic-fallback').encode()
