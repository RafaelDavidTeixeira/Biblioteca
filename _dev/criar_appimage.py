import os, shutil, subprocess, sys

def main():
    base = os.path.expanduser('~/build_appimage')
    appdir = os.path.join(base, 'AppDir')
    os.makedirs(os.path.join(appdir, 'usr/bin'), exist_ok=True)
    os.makedirs(os.path.join(appdir, 'usr/share/icons/hicolor/256x256/apps'), exist_ok=True)
    os.makedirs(os.path.join(appdir, 'usr/share/applications'), exist_ok=True)

    # Copy PyInstaller binary
    shutil.copy(os.path.join(base, 'dist/Biblioteca'), os.path.join(appdir, 'usr/bin/Biblioteca'))

    # Copy icon
    icon_src = '/mnt/d/Projetos DEV/biblioteca_OpenCode/biblioteca/release/biblioteca-icon.png'
    shutil.copy(icon_src, os.path.join(appdir, 'biblioteca-icon.png'))
    shutil.copy(icon_src, os.path.join(appdir, 'usr/share/icons/hicolor/256x256/apps/biblioteca.png'))

    # Desktop file
    desktop = (
        '[Desktop Entry]\n'
        'Name=Biblioteca\n'
        'Comment=Sistema de Controle de Acervo\n'
        'Exec=Biblioteca\n'
        'Icon=biblioteca-icon\n'
        'Terminal=false\n'
        'Type=Application\n'
        'Categories=Education;\n'
        'StartupNotify=true\n'
    )
    with open(os.path.join(appdir, 'biblioteca.desktop'), 'w') as f:
        f.write(desktop)
    shutil.copy(os.path.join(appdir, 'biblioteca.desktop'), os.path.join(appdir, 'usr/share/applications/'))

    # AppRun
    apprun = (
        '#!/bin/bash\n'
        'APPDIR="$(dirname "$(readlink -f "$0")")"\n'
        'export PATH="$APPDIR/usr/bin:$PATH"\n'
        'exec "$APPDIR/usr/bin/Biblioteca" "$@"\n'
    )
    with open(os.path.join(appdir, 'AppRun'), 'w') as f:
        f.write(apprun)
    os.chmod(os.path.join(appdir, 'AppRun'), 0o755)

    print('AppDir created:')
    for root, dirs, files in os.walk(appdir):
        for f in files:
            path = os.path.join(root, f)
            print(' ', os.path.relpath(path, appdir))

    # Download appimagetool
    tool_path = os.path.join(base, 'appimagetool-x86_64.AppImage')
    if not os.path.exists(tool_path):
        print('\nDownloading appimagetool...')
        subprocess.run(['wget', '-q',
            'https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage',
            '-O', tool_path], check=True)
        os.chmod(tool_path, 0o755)

    # Extract appimagetool (no FUSE needed)
    tool_dir = os.path.join(base, 'appimagetool-extracted')
    if not os.path.exists(tool_dir):
        print('\nExtracting appimagetool...')
        subprocess.run([tool_path, '--appimage-extract'], check=True, cwd=base)
        shutil.move(os.path.join(base, 'squashfs-root'), tool_dir)

    # Generate AppImage
    print('\nGenerating AppImage...')
    env = os.environ.copy()
    env['ARCH'] = 'x86_64'
    result = subprocess.run(
        [os.path.join(tool_dir, 'AppRun'), appdir],
        capture_output=True, text=True, cwd=base, env=env
    )
    print(result.stdout)
    if result.returncode != 0:
        print('STDERR:', result.stderr)
        sys.exit(1)

    # Find generated AppImage
    import glob
    appimages = glob.glob(os.path.join(base, '*x86_64.AppImage'))
    if appimages:
        src = appimages[0]
        dst = '/mnt/d/Projetos DEV/biblioteca_OpenCode/biblioteca/release/Biblioteca-x86_64.AppImage'
        shutil.copy(src, dst)
        size = os.path.getsize(dst)
        print(f'\nAppImage generated: {dst} ({size // 1048576} MB)')
    else:
        print('\nAppImage not found in output')
        sys.exit(1)

if __name__ == '__main__':
    main()
