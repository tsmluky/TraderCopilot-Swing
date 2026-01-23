Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ROOT = Join-Path $HOME "Desktop\TraderCopilot"
$BACK = Join-Path $ROOT "backend"

if (-not (Test-Path $BACK)) {
    throw "No encuentro backend en: $BACK"
}

Set-Location $BACK

"== TraderCopilot · Evaluación LITE =="
"Base: $BACK"
""

# Si tienes .venv, puedes usarlo aquí:
# $venvPython = Join-Path $BACK ".venv\Scripts\python.exe"
# if (Test-Path $venvPython) {
#     & $venvPython ".\evaluated_logger.py"
# } else {
#     "No se encontró .venv, usando 'python' global..."
#     python ".\evaluated_logger.py"
# }

python ".\evaluated_logger.py"

"`n== Evaluación LITE completada =="
