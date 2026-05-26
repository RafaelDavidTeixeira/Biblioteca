#!/bin/bash
set -euo pipefail

# ── Versionamento ──
VERSION_FILE='/mnt/d/Projetos DEV/biblioteca_OpenCode/biblioteca/_dev/version.txt'
if [ -f "$VERSION_FILE" ]; then
    VER=$(cat "$VERSION_FILE" | tr -d ' \n')
else
    VER="1.0.0"
fi
# Incrementa patch
VER="${VER%.*}.$((${VER##*.}+1))"
echo "$VER" > "$VERSION_FILE"
# Atualiza app/version.py
echo "VERSION = \"$VER\"" > '/mnt/d/Projetos DEV/biblioteca_OpenCode/biblioteca/app/version.py'
echo "Versao: $VER"

echo "=== 1. Python 3.12 standalone ==="
if [ ! -f /tmp/py312/python/bin/python3.12 ]; then
    curl -fsSL 'https://github.com/indygreg/python-build-standalone/releases/download/20241002/cpython-3.12.7+20241002-x86_64-unknown-linux-gnu-install_only.tar.gz' -o /tmp/py312.tar.gz
    mkdir -p /tmp/py312
    tar xzf /tmp/py312.tar.gz -C /tmp/py312
fi

echo "=== 2. Venv + deps ==="
/tmp/py312/python/bin/python3.12 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install -q flask flask-login flask-sqlalchemy pyinstaller werkzeug pillow python-barcode

echo "=== 3. Copy project ==="
rm -rf /tmp/bib
cp -r '/mnt/d/Projetos DEV/biblioteca_OpenCode/biblioteca' /tmp/bib

echo "=== 4. PyInstaller ==="
cd /tmp/bib
/tmp/venv/bin/pyinstaller Biblioteca.spec --clean 2>&1 | tail -5

echo "=== 5. AppDir ==="
APPDIR=/tmp/AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp /tmp/bib/dist/Biblioteca "$APPDIR/usr/bin/Biblioteca"

python3 << 'PYEOF'
from PIL import Image
Image.new('RGBA', (256,256), (0,80,160,255)).save('/tmp/AppDir/biblioteca-icon.png')
PYEOF

cat > "$APPDIR/Biblioteca.desktop" << 'DESKTOP'
[Desktop Entry]
Name=Biblioteca
Comment=Sistema de Gerenciamento de Biblioteca
Exec=Biblioteca
Icon=biblioteca-icon
Type=Application
Categories=Education;
Terminal=false
DESKTOP

ln -sf usr/bin/Biblioteca "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

echo "=== 6. appimagetool ==="
if [ ! -f /tmp/aitool ]; then
    wget -q 'https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage' -O /tmp/aitool
    chmod +x /tmp/aitool
fi

echo "=== 7. Generate AppImage ==="
FNAME="Biblioteca-${VER}-x86_64.AppImage"
mkdir -p /tmp/bib/release
cd /tmp

/tmp/aitool "$APPDIR" "/tmp/bib/release/${FNAME}" 2>&1 || (
    echo "FUSE fallback..."
    /tmp/aitool --appimage-extract
    ./squashfs-root/AppRun "$APPDIR" "/tmp/bib/release/${FNAME}"
    rm -rf squashfs-root
)

echo "=== 8. Verify ==="
chmod +x "/tmp/bib/release/${FNAME}"
ls -lh "/tmp/bib/release/${FNAME}"
file "/tmp/bib/release/${FNAME}"

echo "=== 9. Copy to release/linux/ ==="
RELEASE_DIR='/mnt/d/Projetos DEV/biblioteca_OpenCode/biblioteca/release/linux'
mkdir -p "$RELEASE_DIR"

# Copia AppImage
cp "/tmp/bib/release/${FNAME}" "$RELEASE_DIR/"

# ── Script de instalação .desktop ──
# Permite abrir pelo menu de aplicativos e gerenciador de arquivos corretamente
cat > "$RELEASE_DIR/instalar-atalho.sh" << INSTALL
#!/bin/bash
DIR="\$(cd "\$(dirname "\$0")" && pwd)"
APPIMAGE="\$(ls "\$DIR"/Biblioteca-*-x86_64.AppImage 2>/dev/null | head -1)"
if [ -z "\$APPIMAGE" ]; then
    echo "Erro: AppImage nao encontrado em \$DIR"
    exit 1
fi

# Copia AppImage para home se necessário
DEST_DIR="\$HOME/.local/share/Biblioteca"
mkdir -p "\$DEST_DIR"
cp "\$APPIMAGE" "\$DEST_DIR/"
APPNAME=$(basename "$APPIMAGE")
chmod +x "\$DEST_DIR/\$APPNAME"

# Cria script launcher com variáveis de ambiente corretas
cat > "\$DEST_DIR/launch.sh" << 'LAUNCHER'
#!/bin/bash
export DISPLAY="\${DISPLAY:-:0}"
export DBUS_SESSION_BUS_ADDRESS="\${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/\$(id -u)/bus}"
export XDG_RUNTIME_DIR="\${XDG_RUNTIME_DIR:-/run/user/\$(id -u)}"
APPIMG=\$(ls "\$HOME/.local/share/Biblioteca"/Biblioteca-*-x86_64.AppImage 2>/dev/null | head -1)
exec "\$APPIMG" "\$@"
LAUNCHER
chmod +x "\$DEST_DIR/launch.sh"

# Cria ícone
mkdir -p "\$HOME/.local/share/icons"
python3 -c "
try:
    from PIL import Image
    Image.new('RGBA',(256,256),(0,80,160,255)).save('\$HOME/.local/share/icons/biblioteca.png')
except:
    pass
" 2>/dev/null || true

# Cria entrada .desktop
mkdir -p "\$HOME/.local/share/applications"
cat > "\$HOME/.local/share/applications/biblioteca.desktop" << DESKTOP
[Desktop Entry]
Name=Biblioteca
Comment=Sistema de Gerenciamento de Biblioteca
Exec=\$DEST_DIR/launch.sh
Icon=\$HOME/.local/share/icons/biblioteca.png
Type=Application
Categories=Education;
Terminal=false
StartupNotify=true
DESKTOP

chmod +x "\$HOME/.local/share/applications/biblioteca.desktop"
update-desktop-database "\$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "✓ Atalho instalado com sucesso!"
echo "  Agora pode abrir pelo menu de aplicativos ou pelo gerenciador de arquivos."
echo ""
INSTALL
chmod +x "$RELEASE_DIR/instalar-atalho.sh"

# Permissao no AppImage
chmod +x "$RELEASE_DIR/${FNAME}" 2>/dev/null || true

ls -lh "$RELEASE_DIR/"

echo ""
echo "=== DONE ==="
echo "Arquivos gerados em: release/linux/"
echo ""
echo "No Linux, para instalar o atalho (abre pelo gerenciador de arquivos):"
echo "  cd release/linux && bash instalar-atalho.sh"
echo ""
echo "Ou para rodar direto pelo terminal:"
echo "  ./release/linux/Biblioteca-${VER}.sh"
