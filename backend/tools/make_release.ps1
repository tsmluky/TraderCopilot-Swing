# backend/tools/make_release.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..
$ROOT = Get-Location
$STAGE = Join-Path $ROOT "_release_backend"
if (Test-Path $STAGE) { Remove-Item $STAGE -Recurse -Force }
robocopy "$ROOT" $STAGE /E /XD ".venv" "__pycache__" "_release_backend" "logs" ".git" | Out-Null
$OUT = Join-Path $ROOT ("TraderCopilot_BACK_{0}.zip" -f (Get-Date -Format "yyyyMMdd_HHmm"))
if (Test-Path $OUT) { Remove-Item $OUT -Force }
Compress-Archive -Path (Join-Path $STAGE "*") -DestinationPath $OUT
"ZIP backend listo: $OUT"
