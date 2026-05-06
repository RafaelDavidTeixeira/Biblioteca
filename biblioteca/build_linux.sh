#!/bin/bash
echo "BUILD - Biblioteca Sistema (Linux)"
pip install flask werkzeug pyinstaller -q 2>/dev/null || pip install flask werkzeug pyinstaller -q --break-system-packages
rm -rf dist build
pyinstaller \
  --onefile --noconsole --name "biblioteca" \
  --add-data "app/templates:app/templates" \
  --add-data "app/static:app/static" \
  --hidden-import flask \
  --hidden-import werkzeug \
  --hidden-import jinja2 \
  --hidden-import click \
  --hidden-import itsdangerous \
  run.py
if [ -f dist/biblioteca ]; then
    mkdir -p release && cp dist/biblioteca release/ && chmod +x release/biblioteca
    echo "SUCESSO: release/biblioteca"
else echo "ERRO: executavel nao gerado"; fi
