# PowerShell script para gerenciar o servidor Flask
param(
    [string]$Action = "start"
)

$pidFile = "server.pid"
$port = 5000

function Start-Server {
    if (Test-Path $pidFile) {
        $oldPid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($oldPid -and (Get-Process -Id $oldPid -ErrorAction SilentlyContinue)) {
            Write-Host "Servidor já está rodando (PID: $oldPid)" -ForegroundColor Yellow
            return
        }
    }
    
    Write-Host "Iniciando servidor Flask..." -ForegroundColor Green
    $process = Start-Process -FilePath "python" -ArgumentList "run.py" -PassThru -WindowStyle Normal
    $process.Id | Out-File $pidFile
    Write-Host "Servidor iniciado (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "Acesse: http://localhost:$port" -ForegroundColor Cyan
}

function Stop-Server {
    $stopped = $false
    
    # Try to stop by PID file
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            try {
                $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($proc) {
                    Stop-Process -Id $pid -Force
                    Write-Host "Servidor parado (PID: $pid)" -ForegroundColor Green
                    $stopped = $true
                }
            } catch {}
        }
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }
    
    # Also kill any python process running run.py
    $procs = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        try {
            $cmdline = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            $cmdline -like "*run.py*"
        } catch { $false }
    }
    
    foreach ($proc in $procs) {
        try {
            Stop-Process -Id $proc.Id -Force
            Write-Host "Processo python run.py parado (PID: $($proc.Id))" -ForegroundColor Green
            $stopped = $true
        } catch {}
    }
    
    # Also check port 5000
    $netProcs = netstat -ano | Select-String ":$port\s" | ForEach-Object {
        $line = $_ -split '\s+'
        $line[-1]
    } | Select-Object -Unique
    
    foreach ($pid in $netProcs) {
        if ($pid -and $pid -match '^\d+$') {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "Processo na porta $port parado (PID: $pid)" -ForegroundColor Green
                $stopped = $true
            } catch {}
        }
    }
    
    if (-not $stopped) {
        Write-Host "Nenhum servidor encontrado rodando." -ForegroundColor Yellow
    }
}

function Restart-Server {
    Write-Host "Reiniciando servidor..." -ForegroundColor Cyan
    Stop-Server
    Start-Sleep -Seconds 2
    Start-Server
}

switch ($Action.ToLower()) {
    "start" { Start-Server }
    "stop" { Stop-Server }
    "restart" { Restart-Server }
    default {
        Write-Host "Uso: .\server.ps1 [-Action] <start|stop|restart>" -ForegroundColor Cyan
        Write-Host "  start   - Inicia o servidor (padrão)" -ForegroundColor White
        Write-Host "  stop    - Para o servidor" -ForegroundColor White
        Write-Host "  restart - Reinicia o servidor" -ForegroundColor White
    }
}
