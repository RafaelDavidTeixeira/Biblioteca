# Build Windows .exe com versão no nome
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$verFile = "$root\_dev\version.txt"
$verPy = "$root\app\version.py"

# Ler versão atual
$VER = (Get-Content $verFile).Trim()
Write-Host "Versão atual: $VER"

# Atualizar app/version.py
"VERSION = `"$VER`"" | Set-Content $verPy -NoNewline
Write-Host "app/version.py atualizado para $VER"

# Limpar builds anteriores
$buildDir = "$root\build"
$distDir = "$root\dist"
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }

# Build PyInstaller
Set-Location $root
python -m PyInstaller Biblioteca.spec --clean
if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou" }

# Renomear e copiar para release
$exeName = "Biblioteca-$VER.exe"
$exePath = "$distDir\Biblioteca.exe"
$releaseDir = "$root\release\windows"
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
Copy-Item $exePath "$releaseDir\$exeName" -Force
Write-Host "Windows: release/windows/$exeName"

# Incrementar patch
$parts = $VER.Split('.')
$parts[2] = [int]$parts[2] + 1
$newVer = $parts -join '.'
$newVer | Set-Content $verFile -NoNewline
Write-Host "Versão incrementada para: $newVer"

Write-Host "=== BUILD WIN CONCLUÍDO ==="
