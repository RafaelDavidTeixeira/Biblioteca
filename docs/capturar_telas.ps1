$ErrorActionPreference = "Stop"

$ProjectDir = "D:\Projetos DEV\biblioteca_OpenCode\biblioteca"
$Chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$OutDir = "$ProjectDir\docs\img"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# 1. Start server
Write-Host ">>> Iniciando servidor..." -ForegroundColor Cyan
$job = Start-Job -ScriptBlock { python "D:\Projetos DEV\biblioteca_OpenCode\biblioteca\run.py" }
Start-Sleep -Seconds 6

# 2. Criar perfil Chrome temporario para persistir cookie
$profileDir = Join-Path $env:TEMP "chrome_bib_$(Get-Random)"

# 3. Primeiro: fazer login permanente no perfil Chrome
Write-Host ">>> Autenticando Chrome..." -ForegroundColor Cyan
& $Chrome --headless=new --screenshot="$OutDir\_init.png" --window-size=1280,800 `
    --user-data-dir="$profileDir" --disable-gpu --no-sandbox --virtual-time-budget=5000 `
    "http://127.0.0.1:5477/_screen_login?next=/dashboard" 2>$null
Start-Sleep -Seconds 2

# 4. Capturar cada pagina (o cookie de sessao persiste no profileDir)
$pages = @(
    @{n="login";       u="http://127.0.0.1:5477/login"}
    @{n="dashboard";   u="http://127.0.0.1:5477/dashboard"}
    @{n="livros";      u="http://127.0.0.1:5477/livros"}
    @{n="alunos";      u="http://127.0.0.1:5477/alunos"}
    @{n="emprestimos"; u="http://127.0.0.1:5477/emprestimos"}
    @{n="graficos";    u="http://127.0.0.1:5477/graficos"}
    @{n="relatorios";  u="http://127.0.0.1:5477/relatorios"}
    @{n="backup";      u="http://127.0.0.1:5477/backup"}
    @{n="reservas";    u="http://127.0.0.1:5477/reservas"}
    @{n="instituicao"; u="http://127.0.0.1:5477/instituicao"}
    @{n="usuarios";    u="http://127.0.0.1:5477/usuarios"}
)

$results = @()
foreach ($p in $pages) {
    $out = "$OutDir\screen_$($p.n).png"
    Write-Host "  Capturando $($p.n)..." -NoNewline
    try {
        & $Chrome --headless=new --screenshot="$out" --window-size=1280,800 `
            --user-data-dir="$profileDir" --disable-gpu --no-sandbox `
            --virtual-time-budget=6000 $p.u 2>$null
        if (Test-Path $out) {
            $kb = [math]::Round((Get-Item $out).Length/1kb, 1)
            Write-Host " OK ($kb KB)" -ForegroundColor Green
            $results += [PSCustomObject]@{Pagina=$p.n; TamanhoKB=$kb}
        } else {
            Write-Host " FALHOU" -ForegroundColor Red
        }
    } catch {
        Write-Host " ERRO: $_" -ForegroundColor Red
    }
}

# 5. Limpeza
Write-Host ">>> Limpando..." -ForegroundColor Cyan
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -ErrorAction SilentlyContinue -Force
netstat -ano | Select-String ":5477" | ForEach-Object {
    $p2 = [regex]::Match($_, "(\d+)\s*$").Groups[1].Value
    if ($p2 -and $p2 -ne "0") { Stop-Process -Id $p2 -Force -ErrorAction SilentlyContinue }
}
Remove-Item -Recurse -Force $profileDir -ErrorAction SilentlyContinue
Remove-Item "$OutDir\_init.png" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== RESULTADO ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
Write-Host "Total: $($results.Count) imagens em $OutDir" -ForegroundColor Green
