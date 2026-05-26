#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$DIR/Biblioteca-"*"-x86_64" 2>/dev/null
BIN=$(ls "$DIR"/Biblioteca-*-x86_64 2>/dev/null | head -1)
if [ -z "$BIN" ]; then
    echo "Erro: binario Biblioteca nao encontrado em $DIR"
    exit 1
fi
echo "Iniciando Biblioteca..."
exec "$BIN" "$@"
