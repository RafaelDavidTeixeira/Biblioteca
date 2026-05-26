$ErrorActionPreference = "Stop"

# 1. Garantir que selenium esta instalado
$hasSelenium = python -c "import selenium; print('ok')" 2>$null
if ($hasSelenium -ne "ok") {
    Write-Host ">>> Instalando selenium..." -ForegroundColor Cyan
    pip install selenium | Out-Null
}

# 2. Executar script de captura
Write-Host ">>> Executando captura..." -ForegroundColor Cyan
python docs/capturar_telas.py

Write-Host ""
Write-Host "Pronto! Imagens em docs/img/" -ForegroundColor Green
