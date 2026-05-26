# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('app/templates', 'app/templates'), ('app/static', 'app/static')],
    hiddenimports=['flask', 'werkzeug', 'sqlite3', 'threading', 'atexit', 'shutil', 'logging', 'PIL', 'barcode', 'barcode.writer', 'barcode.codex', 'ftfy', 'app.database', 'app.license', 'app.version_control', 'app.routes.auth', 'app.routes.books', 'app.routes.students', 'app.routes.loans', 'app.routes.reports', 'app.routes.settings', 'app.routes.api'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Biblioteca',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
