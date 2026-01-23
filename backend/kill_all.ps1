
Write-Host "🛑 Deteniendo todos los procesos de Python y Uvicorn..." -ForegroundColor Yellow

# Detener procesos de Python
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ Procesos Python detenidos." -ForegroundColor Green

# Detener procesos de Uvicorn (si aparecen con ese nombre)
Get-Process uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ Procesos Uvicorn detenidos." -ForegroundColor Green

# Liberar puerto 8000 explícitamente si sigue ocupado
$port = 8000
$p = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($p) {
    Write-Host "⚠️ Puerto $port todavía ocupado por PID $($p.OwningProcess). Matando..." -ForegroundColor Red
    Stop-Process -Id $p.OwningProcess -Force
    Write-Host "✅ Puerto $port liberado." -ForegroundColor Green
}
else {
    Write-Host "✅ Puerto $port está libre." -ForegroundColor Green
}

Write-Host "🧹 Limpieza completada. Ahora puedes reiniciar el servidor limpio." -ForegroundColor Cyan
