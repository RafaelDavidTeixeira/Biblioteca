@echo off
setlocal enabledelayedexpansion
REM Gera executavel do Gerador de Licencas (Windows)
REM Requer PyInstaller instalado: pip install pyinstaller

chcp 65001 >nul
title Compilando Gerador de Licencas...

echo ========================================
echo  Compilando Gerador de Licencas...
echo ========================================
echo.

REM ── Localizar Python ────────────────────────────────────────────
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
        set PIP="%PROGRAMFILES%\Programs\Python%%V\python.exe" -m pip
        goto :found_python
    )
    if exist "C:\Python%%V\python.exe" (
        set PYTHON="C:\Python%%V\python.exe"
        set PIP="C:\Python%%V\python.exe" -m pip
        goto :found_python
    )
)

REM Tenta WindowsApps (Python Store)
for %%V in (3.14 3.13 3.12 3.11 3.10) do (
    where python%%V >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON=python%%V
        set PIP=python%%V -m pip
        goto :found_python
    )
)

echo [ERRO] Python 3.10+ nao encontrado!
echo.
echo Instale em: https://www.python.org/downloads/
echo Na instalacao, marque: "Add Python to PATH"
echo.
pause
exit /b 1

:found_python
echo [OK] Python: %PYTHON%
%PYTHON% --version
echo.

REM ── Instalar PyInstaller se necessario ──────────────────────────
%PIP% show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/1] Instalando PyInstaller...
    %PIP% install pyinstaller --quiet --no-warn-script-location
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar PyInstaller.
        pause & exit /b 1
    )
) else (
    echo [OK] PyInstaller ja instalado
)
echo.

REM ── Mudar para diretorio _dev e limpar builds anteriores ───────
cd /d "%~dp0"
if exist dist          rmdir /s /q dist 2>nul
if exist build         rmdir /s /q build 2>nul

REM ── Compilar ────────────────────────────────────────────────────
echo [1/1] Gerando executavel...
echo.
%PYTHON% -m PyInstaller --onefile --windowed --name "GeradorLicenca" --distpath "..\release" --add-data "license.py;." --noconfirm "app_licenca.py"

echo.
if exist "..\release\GeradorLicenca.exe" (
    echo ========================================
    echo   SUCESSO!
    echo ========================================
    echo   Gerado em: ..\release\GeradorLicenca.exe
    for %%F in ("..\release\GeradorLicenca.exe") do echo   Tamanho: %%~zF bytes
    echo.
    echo   Envie o arquivo "GeradorLicenca.exe" para qualquer PC
    echo   (Windows, sem necessidade de Python instalado).
    echo.
) else (
    echo ========================================
    echo   FALHA! Verifique os erros acima.
    echo ========================================
    echo.
    echo Causas comuns:
    echo   - Antivirus bloqueando o PyInstaller
    echo   - Sem permissao de escrita na pasta
    echo.
)

pause
