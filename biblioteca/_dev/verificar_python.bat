@echo off
echo.
echo ================================================
echo   VERIFICADOR DE PYTHON - Biblioteca Sistema
echo ================================================
echo.
echo Verificando se o Python esta instalado...
echo.

python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python encontrado:
    python --version
    echo.
    echo Tudo certo! Pode rodar o build_windows.bat
    echo.
    pause
    exit /b 0
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python (py launcher) encontrado:
    py --version
    echo.
    echo Tudo certo! Pode rodar o build_windows.bat
    echo.
    pause
    exit /b 0
)

echo [AVISO] Python nao encontrado no PATH.
echo.
echo Opcoes para instalar:
echo.
echo   OPCAO 1 - Site oficial (recomendado):
echo   1. Acesse: https://www.python.org/downloads/
echo   2. Clique em "Download Python 3.x.x"
echo   3. Execute o instalador
echo   4. IMPORTANTE: Marque "Add Python to PATH" antes de instalar
echo   5. Clique em "Install Now"
echo   6. Reinicie o Prompt de Comando
echo   7. Rode build_windows.bat novamente
echo.
echo   OPCAO 2 - Microsoft Store:
echo   1. Abra a Microsoft Store
echo   2. Pesquise "Python 3.12"
echo   3. Clique em "Obter"
echo   4. Aguarde a instalacao
echo   5. Rode build_windows.bat novamente
echo.
pause
