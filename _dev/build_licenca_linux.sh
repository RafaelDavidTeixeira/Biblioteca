#!/bin/bash
# Gera executavel do Gerador de Licencas (Linux)
# Requer PyInstaller: pip install pyinstaller
# Uso: chmod +x build_licenca_linux.sh && ./build_licenca_linux.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " Compilando Gerador de Licencas..."
echo "========================================"
echo ""

# Verificar Python
PYTHON=$(command -v python3 || command -v python || echo "")
if [ -z "$PYTHON" ]; then
    echo "[ERRO] Python nao encontrado."
    exit 1
fi
echo "[OK] Python: $PYTHON"
$PYTHON --version
echo ""

# Instalar PyInstaller se necessario
if ! $PYTHON -m pip show pyinstaller >/dev/null 2>&1; then
    echo "[1/1] Instalando PyInstaller..."
    $PYTHON -m pip install pyinstaller --quiet
else
    echo "[OK] PyInstaller ja instalado"
fi
echo ""

# Mudar para diretorio _dev
cd "$SCRIPT_DIR"

# Limpar builds anteriores
rm -rf dist build

# Compilar
echo "[1/1] Gerando executavel..."
echo ""
$PYTHON -m PyInstaller --onefile --windowed --name "GeradorLicenca" --distpath "../release" --add-data "license.py:." --noconfirm "app_licenca.py"

echo ""
if [ -f "../release/GeradorLicenca" ]; then
    echo "========================================"
    echo "  SUCESSO!"
    echo "========================================"
    echo "  Gerado em: ../release/GeradorLicenca"
    SIZE=$(du -h "../release/GeradorLicenca" | cut -f1)
    echo "  Tamanho: $SIZE"
    echo ""
    echo "  Envie o arquivo 'GeradorLicenca' para qualquer PC"
    echo "  (Linux, sem necessidade de Python instalado)."
    echo ""
else
    echo "========================================"
    echo "  FALHA! Verifique os erros acima."
    echo "========================================"
    exit 1
fi
