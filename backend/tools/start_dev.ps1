# TraderCopilot · start_dev.ps1 (v0.7 con .env y rutas correctas)
param([int]$Port = 8010)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Directorios base
$TOOLS_DIR   = Split-Path -Parent $MyInvocation.MyCommand.Path   # ...\backend\tools
$BACKEND_DIR = Split-Path $TOOLS_DIR -Parent                     # ...\backend
$ROOT        = Split-Path $BACKEND_DIR -Parent                   # ...\TraderCopilot

Set-Location $ROOT

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "python no está en PATH. Activa el venv o añade Python 3.11+ al PATH."
}

Write-Host "== TraderCopilot · Backend ==" -ForegroundColor Cyan
Write-Host "Root:     $ROOT"        -ForegroundColor DarkGray
Write-Host "Backend:  $BACKEND_DIR" -ForegroundColor DarkGray
Write-Host "Port:     $Port"        -ForegroundColor DarkGray

# Cargar backend\.env en variables de entorno del proceso
$dotenvPath = Join-Path $BACKEND_DIR ".env"
if (Test-Path $dotenvPath) {
    Write-Host "Cargando .env desde: $dotenvPath" -ForegroundColor DarkGray
    (Get-Content $dotenvPath -Raw) -split "`r?`n" | ForEach-Object {
        if ($_ -match '^\s*#') { return }
        if ($_ -match '^\s*$') { return }
        if ($_ -match '^\s*([^=]+?)\s*=\s*(.+)$') {
            $k = $matches[1].Trim()
            $v = $matches[2]
            # Asignación dinámica de variables de entorno
            Set-Item -Path ("Env:{0}" -f $k) -Value $v
        }
    }
} else {
    Write-Host "[AVISO] No se encontró .env en $BACKEND_DIR" -ForegroundColor Yellow
}

python -m uvicorn backend.main:app `
    --reload `
    --host 0.0.0.0 `
    --port $Port `
    --reload-dir "$BACKEND_DIR"
