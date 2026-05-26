#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
APPIMAGE="$(ls "$DIR"/Biblioteca-*-x86_64.AppImage 2>/dev/null | head -1)"
if [ -z "$APPIMAGE" ]; then
    echo "Erro: AppImage nao encontrado em $DIR"
    exit 1
fi

# Copia AppImage para home se necessário
DEST_DIR="$HOME/.local/share/Biblioteca"
mkdir -p "$DEST_DIR"
cp "$APPIMAGE" "$DEST_DIR/"
APPNAME=
chmod +x "$DEST_DIR/$APPNAME"

# Cria script launcher com variáveis de ambiente corretas
cat > "$DEST_DIR/launch.sh" << 'LAUNCHER'
#!/bin/bash
export DISPLAY="${DISPLAY:-:0}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
APPIMG=$(ls "$HOME/.local/share/Biblioteca"/Biblioteca-*-x86_64.AppImage 2>/dev/null | head -1)
exec "$APPIMG" "$@"
LAUNCHER
chmod +x "$DEST_DIR/launch.sh"

# Cria ícone
mkdir -p "$HOME/.local/share/icons"
python3 -c "
try:
    from PIL import Image
    Image.new('RGBA',(256,256),(0,80,160,255)).save('$HOME/.local/share/icons/biblioteca.png')
except:
    pass
" 2>/dev/null || true

# Cria entrada .desktop
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/biblioteca.desktop" << DESKTOP
[Desktop Entry]
Name=Biblioteca
Comment=Sistema de Gerenciamento de Biblioteca
Exec=$DEST_DIR/launch.sh
Icon=$HOME/.local/share/icons/biblioteca.png
Type=Application
Categories=Education;
Terminal=false
StartupNotify=true
DESKTOP

chmod +x "$HOME/.local/share/applications/biblioteca.desktop"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "✓ Atalho instalado com sucesso!"
echo "  Agora pode abrir pelo menu de aplicativos ou pelo gerenciador de arquivos."
echo ""
