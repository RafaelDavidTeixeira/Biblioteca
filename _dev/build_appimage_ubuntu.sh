#!/bin/bash
# build_appimage_ubuntu.sh
# Gera Biblioteca-x86_64.AppImage compativel com Ubuntu 20.04+
# Copie a pasta do projeto para o Linux e rode: bash _dev/build_appimage_ubuntu.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PROJ_DIR=$(pwd)

echo "=============================================="
echo " Build Biblioteca AppImage (Ubuntu 20.04+)"
echo "=============================================="

# ----- Python 3.12 via deadsnakes (linkado contra glibc 2.31) -----
if ! command -v python3.12 &>/dev/null; then
    echo ""
    echo "==> Instalando Python 3.12 (deadsnakes)..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3.12 python3.12-venv python3.12-dev
fi

# ----- Dependencias do sistema -----
echo ""
echo "==> Instalando dependencias do sistema..."
sudo apt-get install -y -qq patchelf fuse libfuse2 wget file

# ----- Virtualenv -----
echo ""
echo "==> Criando virtualenv..."
VENV="$PROJ_DIR/_build_venv"
rm -rf "$VENV"
python3.12 -m venv "$VENV"
source "$VENV/bin/activate"
pip install --upgrade pip

echo ""
echo "==> Instalando dependencias Python..."
pip install flask flask-login flask-sqlalchemy pyinstaller werkzeug

# ----- appimagetool -----
echo ""
echo "==> Baixando appimagetool..."
AITOOL="$PROJ_DIR/appimagetool-x86_64.AppImage"
if [ ! -f "$AITOOL" ]; then
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O "$AITOOL"
    chmod +x "$AITOOL"
fi

# ----- PyInstaller -----
echo ""
echo "==> Compilando executavel com PyInstaller..."
pyinstaller Biblioteca.spec --clean 2>&1 | tail -5

# ----- Preparar AppDir -----
echo ""
echo "==> Montando AppDir..."
APPDIR="$PROJ_DIR/dist/Biblioteca.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -r "$PROJ_DIR/dist/Biblioteca"/* "$APPDIR/usr/bin/"

# Icone + .desktop
if [ -f "$PROJ_DIR/_dev/biblioteca-icon.png" ]; then
    cp "$PROJ_DIR/_dev/biblioteca-icon.png" "$APPDIR/"
else
    # fallback: gerar icone placeholder
    echo "Warning: biblioteca-icon.png nao encontrado, gerando placeholder..."
    python3.12 -c "
from PIL import Image
img = Image.new('RGBA', (256,256), (0,80,160,255))
img.save('$APPDIR/biblioteca-icon.png')
"
fi

cat > "$APPDIR/Biblioteca.desktop" << 'EOF'
[Desktop Entry]
Name=Biblioteca
Comment=Sistema de Gerenciamento de Biblioteca
Exec=Biblioteca
Icon=biblioteca-icon
Type=Application
Categories=Education;
Terminal=false
EOF

ln -sf usr/bin/Biblioteca "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

# ----- AppImage -----
echo ""
echo "==> Gerando AppImage..."
mkdir -p "$PROJ_DIR/release"

# appimagetool precisa de FUSE; fallback se nao disponivel
if "$AITOOL" --version &>/dev/null; then
    "$AITOOL" "$APPDIR" "$PROJ_DIR/release/Biblioteca-x86_64.AppImage"
else
    echo "FUSE indisponivel, extraindo appimagetool..."
    cd "$PROJ_DIR"
    "$AITOOL" --appimage-extract
    ./squashfs-root/AppRun "$APPDIR" "$PROJ_DIR/release/Biblioteca-x86_64.AppImage"
    rm -rf squashfs-root
fi

chmod +x "$PROJ_DIR/release/Biblioteca-x86_64.AppImage"

# ----- Limpeza -----
deactivate 2>/dev/null || true
rm -rf "$VENV" "$AITOOL"

echo ""
echo "=============================================="
echo " SUCESSO!"
ls -lh "$PROJ_DIR/release/Biblioteca-x86_64.AppImage"
echo "=============================================="
echo ""
echo "Para executar:"
echo "  cd $PROJ_DIR"
echo "  ./release/Biblioteca-x86_64.AppImage"
echo ""
echo "Se FUSE nao estiver disponivel:"
echo "  ./release/Biblioteca-x86_64.AppImage --appimage-extract"
echo "  ./squashfs-root/AppRun"
