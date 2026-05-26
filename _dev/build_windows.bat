@echo off
setlocal enabledelayedexpansion
echo.
echo ================================================
echo   BUILD - Biblioteca Sistema (Windows)
echo ================================================
echo.

:: ── Ir para raiz do projeto (pai do diretorio _dev) ──
cd /d "%~dp0.."

:: ── Verificar se run.py existe ──
if not exist "run.py" (
    echo [ERRO] run.py nao encontrado em %CD%
    echo.
    echo Execute o script de dentro da pasta _dev ou da raiz do projeto.
    echo.
    pause
    exit /b 1
)

:: ── Localizar Python ────────────────────────────────────────────
set PYTHON=
set PIP=

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    set PIP=python -m pip
    goto :found_python
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    set PIP=py -m pip
    goto :found_python
)

for %%V in (314 313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set PYTHON="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        set PIP="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" -m pip
        goto :found_python
    )
    if exist "%PROGRAMFILES%\Python%%V\python.exe" (
        set PYTHON="%PROGRAMFILES%\Python%%V\python.exe"
        set PIP="%PROGRAMFILES%\Python%%V\python.exe" -m pip
        goto :found_python
    )
    if exist "C:\Python%%V\python.exe" (
        set PYTHON="C:\Python%%V\python.exe"
        set PIP="C:\Python%%V\python.exe" -m pip
        goto :found_python
    )
)

if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe" (
    set PYTHON="%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe"
    set PIP="%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe" -m pip
    goto :found_python
)

:: Tenta WindowsApps por numeracao
for %%V in (3.14 3.13 3.12 3.11 3.10) do (
    where python%%V >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON=python%%V
        set PIP=python%%V -m pip
        goto :found_python
    )
)

echo [ERRO] Python nao encontrado!
echo.
echo Instale em: https://www.python.org/downloads/
echo Na instalacao, marque: "Add Python to PATH"
echo Depois reinicie o Prompt e rode este script novamente.
echo.
pause
exit /b 1

:found_python
echo [OK] Python: %PYTHON%
%PYTHON% --version
echo.

:: ── Instalar dependencias ────────────────────────────────────────
echo [1/3] Instalando Flask e Werkzeug...
%PIP% install flask werkzeug --quiet --no-warn-script-location
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar Flask. Verifique a conexao com a internet.
    pause & exit /b 1
)

echo [2/3] Instalando PyInstaller...
%PIP% install pyinstaller --quiet --no-warn-script-location
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar PyInstaller.
    pause & exit /b 1
)
echo [OK] Dependencias prontas
echo.

:: ── Localizar pyinstaller ────────────────────────────────────────
set PYINST=%PYTHON% -m PyInstaller

:: ── Limpar builds anteriores ─────────────────────────────────────
if exist dist          rmdir /s /q dist
if exist build         rmdir /s /q build
if exist Biblioteca.spec del /q Biblioteca.spec

:: ── Icone (opcional) ─────────────────────────────────────────────
set ICON_OPT=
if exist "app\static\img\icon.ico" set ICON_OPT=--icon "app\static\img\icon.ico"

:: ── Executar build ───────────────────────────────────────────────
echo [3/3] Gerando executavel (2 a 5 minutos)...
echo.

%PYINST% ^
  --onefile ^
  --noconsole ^
  --name "Biblioteca" ^
  %ICON_OPT% ^
  --add-data "app\templates;app\templates" ^
  --add-data "app\static;app\static" ^
  --hidden-import flask ^
  --hidden-import werkzeug ^
  --hidden-import werkzeug.security ^
  --hidden-import jinja2 ^
  --hidden-import click ^
  --hidden-import itsdangerous ^
  --hidden-import barcode ^
  --collect-all flask ^
  run.py

echo.

:: ── Resultado ────────────────────────────────────────────────────
if exist "dist\Biblioteca.exe" (
    echo ================================================
    echo   SUCESSO!
    echo ================================================
    if not exist release mkdir release
    copy /Y "dist\Biblioteca.exe" "release\Biblioteca.exe" >nul
    echo   Gerado em: release\Biblioteca.exe
    for %%F in ("release\Biblioteca.exe") do echo   Tamanho: %%~zF bytes
    echo.
    echo   Proximos passos:
    echo   1. Copie a pasta "release\" para o PC do cliente
    echo   2. Cliente da duplo clique em Biblioteca.exe
    echo   3. Ative a licenca na tela de login
    echo.
) else (
    echo ================================================
    echo   ERRO: executavel nao gerado
    echo ================================================
    echo.
    echo Causas comuns:
    echo   - Antivirus bloqueando o PyInstaller (desative temporariamente)
    echo   - Sem permissao de escrita na pasta (execute como Administrador)
    echo   - Erro de dependencia (veja o log acima)
    echo.
)
pause
