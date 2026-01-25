# apply_fixes.ps1
# Script de reparación y verificación para TraderCopilot-Swing
# Aplica lógica de corrección y ejecuta tests.

$BackupDate = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "backups_$BackupDate"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

Write-Host "[FIX] Starting Repair Sequence..." -ForegroundColor Cyan

# 1. Backup Critical Files
Write-Host "[BACKUP] Backing up critical files to $BackupDir..."
Copy-Item "database.py" "$BackupDir\"
Copy-Item "routers\advisor.py" "$BackupDir\"
Copy-Item "core\signal_logger.py" "$BackupDir\"
Copy-Item "alembic\versions\a19c2f3b7c11_add_stripe_billing_fields.py" "$BackupDir\"

# 2. Files have been patched by the agent. Verifying checksums/existence...
if (-not (Test-Path "database.py")) { Write-Error "database.py missing!"; exit 1 }

# 3. Clean .pyc and checks
Write-Host "[CLEAN] Removing pycache..."
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 4. Run Pytest
Write-Host "[TEST] Running full suite..." -ForegroundColor Cyan
$env:DATABASE_URL = "sqlite:///:memory:" 
# Force in-memory DB for tests to verify StaticPool fix works
# Note: real tests might use fixture to override this, but this is a good default check.

pytest -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] All tests passed!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "[FAIL] Tests failed." -ForegroundColor Red
    exit 1
}
