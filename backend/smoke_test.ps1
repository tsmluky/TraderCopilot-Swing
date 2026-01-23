Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$backend = "$HOME\Desktop\TraderCopilot\backend"
Set-Location $backend

if (Test-Path ".venv\Scripts\Activate.ps1") {
    . ".venv\Scripts\Activate.ps1"
}

Write-Host "== /health ==" -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET | ConvertTo-Json

Write-Host "`n== /strategies/ ==" -ForegroundColor Cyan
$strategies = Invoke-RestMethod -Uri "http://127.0.0.1:8000/strategies/" -Method GET
$strategies | ConvertTo-Json

Write-Host "`n== Activar rsi_macd_divergence_v1 ==" -ForegroundColor Cyan
$body = @{
    enabled          = $true
    interval_seconds = 60
    tokens           = @("ETH","BTC","SOL")
    timeframes       = @("1h")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/strategies/rsi_macd_divergence_v1" `
                  -Method PATCH -Body $body -ContentType "application/json" | ConvertTo-Json

Write-Host "`n== POST /strategies/rsi_macd_divergence_v1/execute ==" -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://127.0.0.1:8000/strategies/rsi_macd_divergence_v1/execute" `
                  -Method POST | ConvertTo-Json
